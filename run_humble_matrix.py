#!/usr/bin/env python3
"""Humble 同士でベースイメージを変えた DDS 通信確認スクリプト。

各組み合わせごとに docker compose を再ビルド・起動し、listener の
ログから "I heard" を 10 回検出できたかを計測して結果を表示する。
"""
import subprocess
import time
import os
from typing import List, Tuple

# テスト対象のベースイメージ一覧（image, label）
BASE_IMAGES: List[Tuple[str, str]] = [
    ("ros:humble-ros-base", "ros-base"),
    ("osrf/ros:humble-desktop", "desktop"),
    ("ros:humble-ros-base-jammy", "ros-base-jammy"),
]

ROS_DISTRO = "humble"
TARGET_MESSAGES = 10
TIMEOUT_SEC = 30


def run_cmd(cmd: List[str], env: dict) -> None:
    """サブプロセスを実行し、失敗時は例外を投げる。"""
    subprocess.run(cmd, check=True, env=env)


def slug(label: str) -> str:
    return label.replace(":", "-").replace("/", "-")


def count_messages(env: dict) -> int:
    """listener ログを追いかけて "I heard" の出現回数を数える。"""
    proc = subprocess.Popen(
        ["docker", "compose", "logs", "-f", "--no-color", "humble_listener"],
        env=env,
        stdout=subprocess.PIPE,
        text=True,
    )
    count = 0
    start = time.time()
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            if "I heard" in line:
                count += 1
                if count >= TARGET_MESSAGES:
                    break
            if time.time() - start > TIMEOUT_SEC:
                break
    finally:
        proc.terminate()
    return count


def build_base_images() -> None:
    """各ベースイメージに対応する talker/listener イメージを1回ずつビルド。"""
    for base_image, label in BASE_IMAGES:
        tag = f"ros2-humble-fastdds-{slug(label)}"
        env = os.environ.copy()
        env.update(
            {
                "ROS_DISTRO": ROS_DISTRO,
                "BASE_IMAGE_TALKER": base_image,
                "BASE_IMAGE_LISTENER": base_image,
                "IMAGE_TALKER": tag,
                "IMAGE_LISTENER": tag,
            }
        )

        print(f"\n[build] {label} -> {tag}")
        run_cmd(["docker", "compose", "build", "humble_talker", "humble_listener"], env)


def test_pair(talker_image: str, talker_label: str, listener_image: str, listener_label: str) -> int:
    env = os.environ.copy()
    project = f"dds-{slug(talker_label)}-{slug(listener_label)}"
    env.update(
        {
            "ROS_DISTRO": ROS_DISTRO,
            "BASE_IMAGE_TALKER": talker_image,
            "BASE_IMAGE_LISTENER": listener_image,
            "IMAGE_TALKER": f"ros2-humble-fastdds-{slug(talker_label)}",
            "IMAGE_LISTENER": f"ros2-humble-fastdds-{slug(listener_label)}",
            "COMPOSE_PROJECT_NAME": project,
        }
    )

    print(f"\n=== talker: {talker_label} / listener: {listener_label} (project: {project}) ===")
    # 1) 起動（デタッチ）
    run_cmd(["docker", "compose", "up", "-d", "humble_talker", "humble_listener"], env)

    try:
        # 2) ログ計測
        successes = count_messages(env)
        print(f"成功回数: {successes}/{TARGET_MESSAGES}")
    finally:
        # 3) 後片付け
        subprocess.run(
            ["docker", "compose", "down"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return successes


def main() -> None:
    # 先に全ベースイメージをビルド（1回ずつ）
    build_base_images()

    results = []
    for t_image, t_label in BASE_IMAGES:
        for l_image, l_label in BASE_IMAGES:
            successes = test_pair(t_image, t_label, l_image, l_label)
            results.append(((t_label, l_label), successes))

    print("\n==== サマリ ====")
    for (t_label, l_label), count in results:
        print(f"talker={t_label}, listener={l_label}: {count}/{TARGET_MESSAGES}")


if __name__ == "__main__":
    main()
