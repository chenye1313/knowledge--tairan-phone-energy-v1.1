# Agent 函数接口与 RAG 路由

## RAG 路由

| 用户意图 | 首选知识块 | 工具 |
|---|---|---|
| 只问体系边界 | `00-智能体使用总纲.md`、`01-来源边界与术语清洁.md` | 无 |
| 查某个数字含义 | `02-数字五行与阴阳基础.md` | 无 |
| 查两位数组合 | `03-八星磁场完整规则.md` | `phone_energy_fixed_rules.json` |
| 分析一个手机号 | `05-排盘计算与七步判断流程.md`、`06-三数成象与动态组合.md` | `phone_energy_pai_pan.py` |
| 做完整匹配报告 | `05`、`06`、`08`、`09` | `phone_energy_pai_pan.py` |
| 选号设计 | `07-选号设计全规则.md`、`08`、`09` | `phone_energy_selection_rules.json` |
| 选号但无喜用神 | `07`、`10`、`11` | 外部八字工具/联网检索 |
| 要求泰然老师话语/表达 DNA | `12-泰然老师话语体系与表达DNA.md`、`11-质量门与风险改写表.md` | 无 |
| 强断言/敏感问题 | `11-质量门与风险改写表.md` | 无 |
| 问来源依据 | `source-index.md`、`raw/` | 无 |
| 问知识库是否完整/MECE/遗漏 | `MECE覆盖矩阵.md`、`source-index.md`、`README.md` | 无 |
| 问部署/投喂/入口文件 | `README.md`、`智能体加载提示词.md`、`prompts/泰然手机号码数字能量顾问_部署速查卡_v7.8.md` | 无 |
| 问测试/压力测试/上线验收 | `prompts/泰然手机号码数字能量顾问_测试用例_v7.8.md`、`tests/压力测试问题.md`、`prompts/泰然手机号码数字能量顾问_QC-FINAL_v7.8.md` | 无 |
| 问图片/补充图/图中证据 | `assets/`、`source-index.md` | 无 |
| 问工具/JSON/规则副本一致性 | `phone_energy_fixed_rules.json`、`phone_energy_selection_rules.json`、`tools/phone_energy_fixed_rules.json`、`tools/phone_energy_selection_rules.json` | `phone_energy_pai_pan.py --verify-rules --compact` |

## 固定排盘工具

工具：

```bash
python3 tools/phone_energy_pai_pan.py <手机号>
```

用途：

- 验证 11 位手机号。
- 抽取后八位。
- 生成 7 个两数组。
- 生成 6 个三数组。
- 标注 0/5。
- 输出尾二、尾三、尾四。

禁止：

- 不做选号评分。
- 不自行八字排盘。
- 不联网。
- 不输出强结论。

## 规则校验工具

```bash
python3 tools/phone_energy_pai_pan.py --verify-rules --compact
```

期望：

```json
{"expected_pair_count":64,"actual_pair_count":64,"ok":true}
```

## 选号函数契约

函数名：

```text
design_phone_number_candidates
```

输入：

```json
{
  "birth_datetime": "1990-01-01 08:30",
  "birth_place": "杭州",
  "calendar_type": "solar",
  "bazi_yongshen": "fire",
  "bazi_yongshen_status": "user_provided",
  "gender": "female",
  "age_group": "adult",
  "role": "sales",
  "goal": "表达成交和稳定现金流",
  "current_phone": "13812345678",
  "city": "杭州",
  "carrier": "China Mobile",
  "preferred_prefixes": ["138", "139"],
  "search_allowed": false,
  "candidate_count": 3
}
```

输出：

```json
{
  "bazi_yongshen_status": "user_provided",
  "bazi_source_note": "用户直接提供喜用神为火。",
  "tail_digit_logic": "喜用神为火，尾数优先 9；销售目标优先祸害被天医承接。",
  "recommended_tail4_or_tail5": ["7139", "89139"],
  "full_number_examples": ["13889137139"],
  "risk_flags": ["public_availability_not_checked"],
  "availability_status": "not_checked",
  "explanation": "候选结构用于表达成交转财库，仍需固定命盘自检和平台核验。",
  "boundary_note": "号码只作为辅助匹配，不替代经营动作、财务纪律或现实客户开发。"
}
```

## 八字喜用神解析契约

触发：

- 只在选号、换号、设计号码、推荐号码时触发。
- 普通算号观察和完整匹配不要求八字。

输入最小集：

```json
{
  "birth_datetime": "1990-01-01 08:30",
  "birth_place": "杭州",
  "calendar_type": "solar",
  "gender": "female",
  "search_allowed": true
}
```

解析规则：

- 用户已提供 `bazi_yongshen`：标记 `user_provided`，直接用于尾数设计。
- 未提供但允许联网：调用外部八字工具或检索公开排盘/万年历/喜用神线索，标记 `tool_calculated` 或 `public_web_reference`。
- 未提供且不能联网：标记 `missing` 或 `unavailable`，不得凭空给喜用神。
- 八字喜用神只用于选号尾数和结构偏好，不进入普通算号判断。

状态值：

| 值 | 含义 |
|---|---|
| `user_provided` | 用户直接提供喜用神 |
| `tool_calculated` | 外部八字工具给出结果 |
| `public_web_reference` | 公开网页/排盘线索给出结果 |
| `missing` | 信息不足，无法解析 |
| `unavailable` | 联网或工具不可用 |

## availability_status

| 值 | 含义 |
|---|---|
| `not_checked` | 未查可得性 |
| `public_signal_only` | 只查到公开线索 |
| `needs_human_verification` | 需要营业厅/平台人工核验 |
| `unavailable_signal` | 公开线索显示不易获得 |

## 联网边界

可联网：

- 查公开八字排盘、万年历、喜用神线索。
- 查公开号段。
- 查归属地。
- 查运营商公开资料。
- 查公开平台上的可得性线索。

不可联网：

- 抓取私人信息。
- 自动购买号码。
- 冒充用户下单。
- 承诺库存真实存在。
- 把联网结果当命盘依据。
