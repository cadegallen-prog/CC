# 🔄 Self-Perpetuating Workflow System

This system automatically generates your next prompt after each task completes. Perfect for non-coders!

## 🚀 How It Works

1. **You paste a prompt** to an AI agent
2. **Agent completes the task**
3. **Agent runs a command** to mark task complete
4. **System generates your NEXT prompt** automatically
5. **You copy-paste the next prompt** to a new agent
6. Repeat! 🔁

---

## 📋 Quick Start

### Step 1: Check Your Next Prompt

The system always tells you what to do next. Run:

```bash
python scripts/workflow_engine.py next
```

This shows your next copy-paste prompt!

### Step 2: Copy-Paste to AI Agent

Copy the entire prompt and paste it to Claude or another AI agent.

### Step 3: Agent Marks Task Complete

At the end of each prompt, there's a command like this:

```bash
python -c "from workflow_engine import WorkflowEngine; w = WorkflowEngine(); w.mark_task_complete('task_name', {'result': 123})"
```

The agent will run this command, which:
- ✅ Marks the task complete
- 📝 Logs what was done
- 🎯 Generates your NEXT prompt

### Step 4: Get Next Prompt

Run the same command:

```bash
python scripts/workflow_engine.py next
```

Now you have a new prompt! Go to Step 2.

---

## 📊 Checking Status

See what you've completed and what's next:

```bash
python scripts/workflow_engine.py status
```

Output:
```
================================================================================
WORKFLOW STATUS
================================================================================

Current Phase: Stage 1 - Product Classification
Classifier Accuracy: 93.2%
Products Classified: 44/425

Completed Tasks: 2
  1. classify_all_products - 2025-01-15
  2. create_dashboard - 2025-01-15

Next Recommended Action:
  → Check /home/user/CC/workflow/NEXT_PROMPT.txt for your next copy-paste prompt!

================================================================================
```

---

## 🎯 The Workflow Cycle

```
┌──────────────────┐
│  You copy-paste  │
│  prompt to AI    │
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  AI completes    │
│  the task        │
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  AI runs:        │
│  mark_complete() │
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  System generates│
│  NEXT prompt     │
└────────┬─────────┘
         │
         v
┌──────────────────┐
│  You get next    │
│  prompt from:    │
│  workflow/       │
│  NEXT_PROMPT.txt │
└────────┬─────────┘
         │
         └──────────> REPEAT! 🔁
```

---

## 📁 Files Created

The workflow engine creates:

- **`workflow/NEXT_PROMPT.txt`** - Your next copy-paste prompt (always read this!)
- **`workflow/completed_tasks.json`** - Log of all completed tasks
- **`workflow/workflow_state.json`** - Current workflow state
- **`workflow/`** - Directory for all workflow files

---

## 🔧 Manual Task Completion

If you complete a task manually (not through a prompt), you can mark it complete:

```bash
python -c "from scripts.workflow_engine import WorkflowEngine; w = WorkflowEngine(); w.mark_task_complete('my_task_name', {'my_result': 123})"
```

Example:

```bash
cd /home/user/CC
python -c "from scripts.workflow_engine import WorkflowEngine; w = WorkflowEngine(); w.mark_task_complete('classify_all_products', {'classified_count': 425, 'unknown_count': 11, 'avg_confidence': 87.3})"
```

---

## 📖 Example Workflow

### Task 1: Classify All Products

**You run:**
```bash
python scripts/workflow_engine.py next
```

**System shows:**
```
🔄 RECOMMENDED NEXT STEP: Classify All 425 Products

Copy-paste this prompt to a new AI agent:

---
I have a product classifier at 93.2% accuracy...
[full prompt]
---
```

**You:** Copy-paste to Claude

**Claude:** Completes task, then runs:
```bash
python -c "from workflow_engine import WorkflowEngine; w = WorkflowEngine(); w.mark_task_complete('classify_all_products', {'classified_count': 425, 'unknown_count': 11, 'avg_confidence': 87.3})"
```

**System:** Generates next prompt automatically!

---

### Task 2: Create Dashboard

**You run:**
```bash
python scripts/workflow_engine.py next
```

**System shows:**
```
🔄 RECOMMENDED NEXT STEP: Create Visualization Dashboard

Now that all products are classified, create a dashboard...
[full prompt with specifics from previous task]
---
```

**You:** Copy-paste to Claude

**Claude:** Completes task, then runs mark_complete again

**System:** Generates next prompt (quality audit)

---

And so on! The workflow engine knows what you've done and suggests the logical next step.

---

## 🎨 Smart Prompt Generation

The workflow engine generates intelligent prompts based on:

1. **What you just completed** - References your actual results
2. **What's left to do** - Knows the full workflow
3. **Your project state** - Uses your accuracy, counts, etc.
4. **Dependencies** - Won't suggest Stage 2 before Stage 1 is done

Example: If quality audit finds 50 issues, it suggests "Fix Quality Issues" next.
If quality audit finds 2 issues, it suggests "Start Stage 2" next.

---

## 🛠️ Customizing Prompts

You can edit `scripts/workflow_engine.py` to:

- Add new task types
- Customize prompt templates
- Change workflow logic
- Add new phases

Each task has a prompt generator function like:
```python
def _prompt_after_classification(self, results):
    # Generate smart prompt using results
    return prompt
```

---

## ⚡ Quick Commands

```bash
# See status
python scripts/workflow_engine.py status

# Get next prompt
python scripts/workflow_engine.py next

# Mark task complete manually
python scripts/workflow_engine.py complete task_name

# See all completed tasks
cat workflow/completed_tasks.json | python -m json.tool
```

---

## 🎯 Benefits

### For You (Non-Coder):
- ✅ **Never wonder "what's next?"** - System tells you
- ✅ **Copy-paste simplicity** - No coding required
- ✅ **Context preserved** - Next prompt knows what you did
- ✅ **Track progress** - See completed tasks
- ✅ **Smart suggestions** - Prompts adapt to your results

### For AI Agents:
- ✅ **Clear completion criteria** - Knows when done
- ✅ **Self-documenting** - Each task logs results
- ✅ **Chainable** - Output becomes next input
- ✅ **Parallel-safe** - Different tasks don't conflict

---

## 🌟 Advanced: Parallel Workflows

You can run multiple workflows in parallel! The engine tracks each separately:

```bash
# Workflow A: Quality improvements
Agent A completes → quality_audit
Agent B completes → fix_errors

# Workflow B: Stage 2 progression
Agent C completes → taxonomy_mapping
Agent D completes → generate_docs

# Engine knows which tasks are done
# Suggests next steps for BOTH workflows
```

---

## 📚 Next Steps

1. **Run your first workflow:**
   ```bash
   python scripts/workflow_engine.py next
   ```

2. **Copy-paste the prompt** to Claude

3. **Watch the magic happen!** ✨

Each completion automatically generates the next prompt. You just copy-paste and go!

---

**Questions?** The workflow engine is self-documenting. Read:
- `scripts/workflow_engine.py` - Main engine code
- `workflow/NEXT_PROMPT.txt` - Always has your next action
- `workflow/completed_tasks.json` - Your progress log
