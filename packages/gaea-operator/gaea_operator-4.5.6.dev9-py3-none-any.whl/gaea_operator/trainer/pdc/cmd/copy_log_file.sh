#!/bin/bash

# 定义轮询和复制文件的函数
poll_and_copy_files() {
    local source_dir=$1
    local destination_dir=$2

    # 检查源目录和目标目录是否存在
    if [ ! -d "$source_dir" ]; then
        echo "Source directory $source_dir does not exist."
        return 1
    fi
    if [ ! -d "$destination_dir" ]; then
        echo "Destination directory $destination_dir does not exist."
        return 1
    fi

    # 查找源目录中所有文件并复制到目标目录
    for file in "$source_dir"/*; do
        # 检查文件是否为普通文件
        if [ -f "$file" ]; then
            # 提取文件名
            filename=$(basename "$file")
            # 构建目标路径
            destination_path="$destination_dir/$filename"
            # 如果目标路径不存在，则复制文件
            \cp -f "$file" "$destination_path"
        fi
    done
}


# 定义轮询函数
poll_files() {
    local source_dir=$1
    local destination_dir=$2
    local poll_interval=$3

    while true; do
        poll_and_copy_files "$source_dir" "$destination_dir"
        sleep $poll_interval
    done
}

# 示例用法：调用轮询函数并传入源目录、目标目录和轮询间隔
source_directory=`pwd`/log
destination_directory=$1
poll_interval=20 # 轮询间隔时间（秒）
poll_files "$source_directory" "$destination_directory" $poll_interval

