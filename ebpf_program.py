ebpf_program_text = """
// define output data structure in C
enum Operation {
    READ = 1,
    WRITE = 2
};

struct data_output_t {
    int pid;
    u64 ts;
    char comm[16];
    enum Operation op;
};

BPF_PERF_OUTPUT(events);

enum InputParam {
    UID = 1,
    PID = 2
};

BPF_HASH(input_table, enum InputParam, int);

int trace_sys_read(struct pt_regs *ctx) {
    int pid = bpf_get_current_pid_tgid() >> 32;
    int uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    int target_pid = %PID_TO_TRACE%;
    int target_uid = %UID_TO_TRACE%;
    if ((target_pid == -1 || pid == target_pid) && (target_uid == -1 || uid == target_uid)) {
        struct data_output_t data = {};
    
        data.op = READ;
        data.pid = pid;
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
        events.perf_submit(ctx, &data, sizeof(data));
        return 0;
    }
}

int trace_sys_write(void *ctx) {
    int pid = bpf_get_current_pid_tgid() >> 32;
    int uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
    int target_pid = %PID_TO_TRACE%;
    int target_uid = %UID_TO_TRACE%;
    if ((target_pid == -1 || pid == target_pid) && (target_uid == -1 || uid == target_uid)) {
        struct data_output_t data = {};
    
        data.op = WRITE;
        data.pid = pid;
        data.ts = bpf_ktime_get_ns();
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
        events.perf_submit(ctx, &data, sizeof(data));
        return 0;
    }
}
"""