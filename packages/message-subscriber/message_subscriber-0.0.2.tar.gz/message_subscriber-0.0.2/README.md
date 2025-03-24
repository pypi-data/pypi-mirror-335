# MessageSubscriber

## 概述
`MessageSubscriber` 是一个用于处理消息订阅的组件。它允许应用程序接收和处理来自不同消息源的实时消息。

## 功能
- **实时消息接收**: 通过 WebSocket 或其他协议实时接收消息。
- **消息处理**: 提供灵活的消息处理机制，可以根据消息类型执行不同的操作。
- **错误处理**: 内置错误处理机制，确保在消息接收过程中出现问题时能够妥善处理。

## 发布
1. 进入frontent执行npm run build
2. 进入setup.py目录执行 python setup.py sdist bdist_wheel
3. 执行运行 Upload PiPy Task

## 安装
使用 npm 或 yarn 安装组件：
```bash
npm install message_subscriber
# 或者
yarn add message_subscriber
```

## 使用示例
```javascript
import MessageSubscriber from 'message_subscriber';

const App = () => {
    return (
        <MessageSubscriber onMessage={(msg) => console.log(msg)} />
    );
};
```

## API
### Props
- `onMessage`: (function) 当接收到新消息时调用的回调函数。
- `url`: (string) 消息源的 URL。

## 贡献
欢迎任何形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 以获取更多信息。

## 许可证
该项目遵循 MIT 许可证。有关详细信息，请参阅 [LICENSE](LICENSE) 文件。