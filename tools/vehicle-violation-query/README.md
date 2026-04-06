# 车辆违章查询工具

## 概述
这是一个车辆交通违章查询工具的演示版本，提供直观的界面来查询车辆违章记录。

## 功能特点
- ✅ 支持全国主要城市车辆查询
- ✅ 显示详细违章信息（时间、地点、类型）
- ✅ 清晰展示扣分和罚款金额
- ✅ 车牌号格式自动验证
- ✅ 简洁直观的界面设计
- ✅ 快速响应，即时查询结果

## 文件说明
- `app.html` - 工具功能页面（实际使用页面）
- `index.html` - 工具详情介绍页面

## 当前状态
⚠️ **演示版本**：当前版本使用模拟数据展示界面交互效果。

## 接入真实API

要将其转换为生产环境可用的工具，需要完成以下步骤：

### 1. 选择API提供商
可选的API服务：
- 各地交通管理部门官方API
- 第三方车辆信息查询服务
- 自建后端服务对接交管系统

### 2. 修改查询逻辑
在 `app.html` 中的 `queryViolation()` 函数中，将模拟数据替换为真实的API调用：

```javascript
// 示例：替换为真实API调用
async function queryViolation() {
    if (!validateInput()) {
        return;
    }

    queryBtn.disabled = true;
    queryBtn.textContent = '查询中...';
    
    try {
        const response = await fetch('YOUR_API_ENDPOINT', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer YOUR_API_KEY'
            },
            body: JSON.stringify({
                plateNumber: plateNumberInput.value.trim(),
                vin: vinInput.value.trim(),
                engineNo: engineNoInput.value.trim(),
                region: regionSelect.value
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            renderViolations(data.violations);
            showMessage('查询成功！', 'success');
        } else {
            showMessage(data.message || '查询失败', 'error');
        }
    } catch (error) {
        showMessage('网络错误，请稍后重试', 'error');
        console.error('Query error:', error);
    } finally {
        queryBtn.disabled = false;
        queryBtn.textContent = '查询违章';
    }
}
```

### 3. API返回数据格式
建议API返回以下格式的数据：

```json
{
  "success": true,
  "violations": [
    {
      "type": "闯红灯",
      "location": "中山路与解放路交叉口",
      "date": "2024-01-15 14:30",
      "points": 6,
      "fine": 200
    }
  ]
}
```

### 4. 安全注意事项
- ⚠️ API密钥不应硬编码在前端代码中
- ⚠️ 建议使用后端代理来保护API密钥
- ⚠️ 实现请求频率限制，防止滥用
- ⚠️ 添加用户身份验证机制
- ⚠️ 遵守相关法律法规和数据隐私政策

## 本地测试

1. 在项目根目录启动本地服务器：
```bash
python -m http.server 8000
```

2. 访问：`http://localhost:8000/tools/vehicle-violation-query/app.html`

## 部署

将文件上传到静态托管服务即可：
- GitHub Pages
- Vercel
- Netlify
- 任何支持静态文件的Web服务器

## 贡献

欢迎提交改进建议或Bug报告！

## 许可

本项目遵循 JustHTMLs 项目的开源协议。
