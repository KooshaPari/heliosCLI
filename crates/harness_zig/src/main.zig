// Zig implementation for heliosHarness - Low-level operations
// High-performance string processing and memory operations

const std = @import("std");

/// Fast string hash - useful for cache keys
export fn zig_hash(s: [*:0]const u8) u32 {
    var hash: u32 = 5381;
    var i: usize = 0;
    while (s[i] != 0) : (i += 1) {
        hash = ((hash << 5) + hash) + s[i]; // hash * 33 + c
    }
    return hash;
}

/// Fast memory copy - optimized
export fn zig_memcpy(dest: [*]u8, src: [*]const u8, len: usize) void {
    @memcpy(dest, src, len);
}

/// Fast string compare
export fn zig_strcmp(a: [*:0]const u8, b: [*:0]const u8) i32 {
    var i: usize = 0;
    while (a[i] != 0 and b[i] != 0) : (i += 1) {
        if (a[i] != b[i]) {
            return if (a[i] > b[i]) 1 else -1;
        }
    }
    return if (a[i] == b[i]) 0 else if (a[i] == 0) -1 else 1;
}

pub fn main() !void {
    std.debug.print("Zig low-level ops ready\n", .{});
}
