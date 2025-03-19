while true; do
    # 调用 paddlecloud job list 命令，并将结果存储到临时文件 job_info.txt 中
    paddlecloud job --ak $1 --sk $2 list --job-name $3 > job_info.txt

    # 解析 job_info.txt 文件，获取 jobStatus 字段的值
    job_status=$(grep -oP 'jobStatus:\s*\K\w+' job_info.txt)

    # 判断 jobStatus 是否为 fail，success，kill_submit，killing，killed 中的任意一个
    if [[ $job_status =~ ^(fail|success|kill_submit|killing|killed)$ ]]; then
        echo "Job 状态为 $job_status, 任务结束。"
        if [[ $job_status == "success" ]]; then
          exit 0
        fi
        exit $job_status
    fi

    sleep 60
done