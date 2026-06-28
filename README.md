# Knowledge Repository Guide

Skill name: `泰然手机号码数字能量知识库 v1.1`

Read this file first before choosing a more specific knowledge file.

## Topic Routing

- `knowledge/03-八星磁场完整规则.md`: 天医、生气、延年、绝命、五鬼、六煞、祸害、伏位、两数组合、固定命盘
- `knowledge/05-排盘计算与七步判断流程.md`: 排盘、怎么算、后八位、尾二、尾三、尾四、结构观察
- `knowledge/07-选号设计全规则.md`: 选号、换号、推荐号码、喜用神、八字、职业组合
- `knowledge/10-Agent函数接口与RAG路由.md`: 函数、RAG、路由、工具、接口、联网、JSON
- `knowledge/11-质量门与风险改写表.md`: 一定、必然、铁口、离婚、破财、疾病、血光、风险、边界
- `knowledge/12-泰然老师话语体系与表达DNA.md`: 语气、表达DNA、口吻、怎么说、泰然老师怎么讲
- `source-index.md`: 出处、依据、来源、核验、MECE、有没有遗漏

## Rules

- 先读 README.md 和 智能体加载提示词.md，再根据问题最小化调用所需文件。
- 涉及具体号码、排盘、尾号、0/5、两数组、三数组局时，优先使用固定规则和排盘流程。
- 涉及选号、换号、推荐号码时，必须处理 bazi_yongshen；没有喜用神时必须联网或调用外部八字工具，不得凭空推断。
- 回答时把知识吸收到当前 bot 语气里，不要暴露知识库、文件名、operation 名或调用过程。
- 先看人，再看号；信息不足时只给结构观察版，不做完整匹配结论。
