ARG ROS_DISTRO=humble
FROM ros:${ROS_DISTRO}-ros-base

ENV DEBIAN_FRONTEND=noninteractive

# デモ用ノードと Fast DDS 実装を追加
RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-demo-nodes-cpp \
    ros-${ROS_DISTRO}-demo-nodes-py \
    ros-${ROS_DISTRO}-rmw-fastrtps-cpp \
    ros-${ROS_DISTRO}-rmw-fastrtps-dynamic-cpp \
    && rm -rf /var/lib/apt/lists/*

# Fast DDS をデフォルトに固定
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# Fast DDS の動作プロファイルを配置（必要に応じて調整してください）
WORKDIR /root
COPY fastdds_profiles.xml /root/fastdds_profiles.xml
ENV FASTRTPS_DEFAULT_PROFILES_FILE=/root/fastdds_profiles.xml

CMD ["bash"]
