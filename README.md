# Long-form Fiction Skills

一套面向 Codex 的长篇小说续写 Skill 工作流。它把原始章节、故事 Wiki、风格包、分层规划和正文写作分开管理，并通过 `storyctl` 状态机阻止跳过关键步骤。

## 能力

- 从原作和已批准续写中维护人物、时间线、世界规则、关系与伏笔 Wiki。
- 从用户提供的文本提炼项目级风格包，包括叙事结构、电影化场景、情绪节奏、人物声音、意象和标题系统。
- 规划全书、篇章、章节序列和具体章节，并保存结构化用户决定。
- 根据批准大纲、最新 Wiki 和风格包撰写章节。
- 支持有边界的托管模式：篇章和章节序列批准后，可自动规划、写作、验收和回写若干小章节；重大决定仍会暂停询问用户。

## 目录

```text
novel-workflow/   总控与流程路由
novel-wiki/       故事 Wiki 维护
novel-style/      风格分析与风格包维护
novel-planning/   篇章、多线、张力与章节规划
novel-writing/    电影化场景、多线剪辑与正文写作
storyctl/         标准库 Python 状态机 CLI
story-workspace-template/  空白故事工程模板
```

仓库不包含任何小说原文、现成续写、项目 Wiki 或私人创作资料。

## 项目级安装

把仓库克隆到小说项目中，然后建立项目级 Skill 链接：

```bash
git clone https://github.com/Zero-Ricardo/-skill.git .fiction-skills
mkdir -p .agents/skills

for skill in novel-workflow novel-wiki novel-style novel-planning novel-writing; do
  ln -s "../../.fiction-skills/$skill" ".agents/skills/$skill"
done
```

Codex 支持项目级 `.agents/skills`。如果新 Skill 没有立即出现，重新打开项目或重启 Codex。

## 初始化故事工程

从小说项目根目录执行：

```bash
python3 .fiction-skills/storyctl/storyctl.py --root . init
python3 .fiction-skills/storyctl/storyctl.py --root . validate
```

然后把合法持有的原始章节放入：

```text
sources/canon/
```

可以直接用自然语言开始，例如：

```text
读取 sources/canon 中的原作章节，整理并建立小说 Wiki。
```

`novel-workflow` 默认允许隐式触发，其他 Skill 由总控按状态路由。

## 标准工作流

```text
原作章节
  → Wiki 更新
  → 风格观察与风格包确认
  → 篇章/章节方案
  → 用户结构化确认
  → 正文草稿
  → 用户批准
  → Wiki 回写
```

核心状态命令：

```bash
storyctl status
storyctl check-ready-to-plan
storyctl check-ready-to-write <plan-id>
storyctl validate
```

实际使用时可调用 `storyctl/storyctl`，或直接运行 `python3 storyctl/storyctl.py`。

## 托管模式

托管模式不是取消所有约束，而是让用户在批准篇章总纲和章节序列后，一次性授予有限范围的章节级决策权。

启用示例：

```bash
storyctl managed-enable \
  --arc-id book-2 \
  --sequence-id book-2-sequence \
  --chapter book-2-ch01 \
  --chapter book-2-ch02 \
  --chapter book-2-ch03 \
  --max-chapters 3
```

托管循环通过以下命令获取唯一合法的下一动作：

```bash
storyctl managed-next
storyctl managed-status
```

可用控制命令：

```bash
storyctl managed-pause --reason <reason> [--chapter <id>]
storyctl managed-resume [--decision <decision-file>]
storyctl managed-disable
```

默认硬暂停事项包括：正史冲突、偏离篇章结局、主要人物死亡或背叛、身份揭晓、世界规则改变、核心谜团或重大伏笔回收、关系状态改变、新能力以及低置信度决策。

委托批准不会伪装成逐章用户批准。决定记录会明确标注：

```yaml
confirmed_by: delegation
delegation_id: managed-book-2-...
```

每个托管正文还必须通过结构化质量报告，并且最多自动修订两次。Wiki 回写始终是下一章之前的强制步骤。

## 风格边界

风格 Skill 用于从用户提供的文本中提炼高层、可复用的叙事特点，不应复制在世作者的独特措辞，也不应把 AI 续写自动当作原作风格证据。候选风格规则需要用户确认后才会进入正式上下文。

## 验证

运行状态机测试：

```bash
python3 -m unittest discover -s storyctl/tests -v
```

测试覆盖：

- Wiki 未更新时禁止规划；
- 未确认方案时禁止正式化大纲；
- 过期方案拒绝批准；
- 风格包只加载已批准文件；
- 托管授权、委托批准和质量报告；
- 批次上限暂停与逐章 Wiki 回写。

## 数据与版权

不要将无权分发的原作文本、私人 Wiki、草稿、决策记录或续写内容提交到本仓库。建议让 Skill/CLI 与具体小说工程分仓管理。
