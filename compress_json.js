#!/usr/bin/env node
/**
 * 使用json-url('lzma')压缩JSON数据
 * 这与ray-optics仿真器使用的格式完全一致
 */

const codec = require('json-url')('lzma');

// 从stdin读取JSON数据
let inputData = '';

process.stdin.on('data', (chunk) => {
    inputData += chunk;
});

process.stdin.on('end', async () => {
    try {
        // 解析JSON
        const jsonData = JSON.parse(inputData);

        // 使用json-url的lzma编解码器压缩
        const compressed = await codec.compress(jsonData);

        // 输出压缩后的字符串
        process.stdout.write(compressed);

    } catch (error) {
        console.error('压缩失败:', error.message);
        process.exit(1);
    }
});
