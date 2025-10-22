# Graph结构修复说明

## 问题描述
导出的工作流导入到Dify后，节点显示为白色且不可用。

## 根本原因
导出的graph结构与Dify官方导出格式存在多处差异。

## 对比分析

### 1. Version字段
```yaml
# 修复前
version: '1.0'

# 修复后（与Dify官方一致）
version: 0.4.0
```

### 2. 节点结构差异

#### 修复前（不完整）
```yaml
nodes:
  - id: start
    type: start
    position: {x: 100, y: 100}
    data:
      type: start
      title: 开始
```

#### 修复后（完整）
```yaml
nodes:
  - id: start
    type: custom              # ✅ 必须是custom
    position: {x: 100, y: 100}
    positionAbsolute: {x: 100, y: 100}  # ✅ 添加绝对位置
    sourcePosition: right     # ✅ 添加连接点位置
    targetPosition: left      # ✅ 添加连接点位置
    width: 244                # ✅ 添加节点宽度
    height: 54                # ✅ 添加节点高度
    selected: false           # ✅ 添加选中状态
    data:
      type: start             # ✅ 保留原始类型
      title: 开始
      desc: ''                # ✅ 添加描述
      selected: false         # ✅ 添加选中状态
      variables: []
```

### 3. 边结构差异

#### 修复前（不完整）
```yaml
edges:
  - id: start-llm
    source: start
    target: llm
    source_handle: source
    target_handle: target
```

#### 修复后（完整）
```yaml
edges:
  - id: start-llm
    source: start
    target: llm
    sourceHandle: source
    targetHandle: target
    type: custom              # ✅ 必须是custom
    zIndex: 0                 # ✅ 添加层级
    data:
      sourceType: start       # ✅ 添加源节点类型
      targetType: llm         # ✅ 添加目标节点类型
      isInLoop: false         # ✅ 添加是否在循环中
```

### 4. 添加viewport字段
```yaml
graph:
  nodes: [...]
  edges: [...]
  viewport:                   # ✅ 添加视口信息
    x: 0
    y: 0
    zoom: 1
```

## 修复实现

### `_normalize_graph()` 方法功能

1. **节点规范化**
   - ✅ 将所有节点type改为 `custom`
   - ✅ 添加 `positionAbsolute`（与position相同）
   - ✅ 添加 `sourcePosition` 和 `targetPosition`
   - ✅ 根据节点类型设置合适的 `width` 和 `height`
   - ✅ 在data中添加 `desc` 和 `selected` 字段
   - ✅ 保留原始节点类型在 `data.type` 中

2. **边规范化**
   - ✅ 将所有边type改为 `custom`
   - ✅ 添加 `zIndex` 字段
   - ✅ 在data中添加 `sourceType` 和 `targetType`（从节点推断）
   - ✅ 添加 `isInLoop` 字段

3. **添加viewport**
   - ✅ 添加默认的viewport配置

## 节点高度规则

```python
if node_type == "start":
    height = 54
elif node_type == "answer":
    height = 105
else:
    height = 90  # LLM, 工具等其他节点
```

## 完整导出示例

```yaml
version: 0.4.0
kind: app
app:
  name: '测试工作流'
  mode: advanced-chat
  icon: 🤖
  icon_background: '#FFEAD5'
  description: ''
  use_icon_as_answer_icon: false
workflow:
  version: '1.0'
  graph:
    nodes:
    - id: '1760152146487'
      type: custom
      position: {x: 80, y: 282}
      positionAbsolute: {x: 80, y: 282}
      sourcePosition: right
      targetPosition: left
      width: 244
      height: 54
      selected: false
      data:
        type: start
        title: 开始
        desc: ''
        selected: false
        variables: []
    - id: llm
      type: custom
      position: {x: 680, y: 282}
      positionAbsolute: {x: 680, y: 282}
      sourcePosition: right
      targetPosition: left
      width: 244
      height: 90
      selected: true
      data:
        type: llm
        title: LLM
        desc: ''
        selected: true
        model:
          provider: openai
          name: gpt-3.5-turbo
          mode: chat
        prompt_template:
        - role: system
          text: 回答用户问题
    edges:
    - id: 1760152146487-source-llm-target
      source: '1760152146487'
      target: llm
      sourceHandle: source
      targetHandle: target
      type: custom
      zIndex: 0
      data:
        sourceType: start
        targetType: llm
        isInLoop: false
    viewport:
      x: 0
      y: 0
      zoom: 1
  features:
    file_upload:
      image:
        enabled: false
        number_limits: 3
        transfer_methods:
        - local_file
        - remote_url
    opening_statement: ''
    suggested_questions: []
    suggested_questions_after_answer:
      enabled: false
    speech_to_text:
      enabled: false
    text_to_speech:
      enabled: false
  environment_variables: []
dependencies: []
```

## 测试步骤

1. **重启后端服务**
   ```bash
   cd backend
   python app.py
   ```

2. **导出工作流**
   - 选择任意工作流导出

3. **检查导出文件**
   - 确认 `version: 0.4.0`
   - 确认节点有 `width`, `height`, `positionAbsolute` 等字段
   - 确认节点 `type: custom`
   - 确认边有 `data.sourceType`, `data.targetType` 等字段
   - 确认边 `type: custom`

4. **导入测试**
   - 将导出的YAML文件导入到Dify
   - 确认节点显示正常（不是白色）
   - 确认可以正常编辑

## 关键要点

1. **type字段的双重含义**
   - 节点外层 `type: custom` - 告诉Dify这是自定义节点
   - 节点data中 `type: start/llm/answer` - 节点的真实类型

2. **position vs positionAbsolute**
   - 通常情况下两者相同
   - 在嵌套容器中可能不同

3. **sourceType 和 targetType**
   - 必须与连接的源节点和目标节点的真实类型一致
   - 使用 `data.type` 的值，不是外层的 `type`

4. **version 0.4.0**
   - 这是Dify当前支持的DSL版本
   - 必须与官方保持一致

---

**修复日期**: 2025-10-22
**修复依据**: Dify官方导出格式对比分析

