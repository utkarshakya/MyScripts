# Universal Script Runner

A powerful, cross-platform tool to run scripts on multiple files in a folder. Supports Python, Node.js, Shell, PowerShell, and custom commands with an intuitive interactive interface.

## 🌟 Features

- **Interactive & CLI Modes**: Choose between guided prompts or command-line automation
- **Smart Script Detection**: Automatically detects interactive scripts and warns you
- **Flexible Argument System**: Use `{FILE}` placeholder to position file path anywhere in your command
- **Multiple Execution Modes**: Capture, Pass-through, and Interactive modes for different scenarios
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Beautiful UI**: Colored output, progress bars, and rich formatting (when enhanced mode is enabled)
- **Robust Error Handling**: Timeouts, detailed error messages, and execution summaries

---

## 📦 Installation

### Prerequisites
- Python 3.6 or higher

### First Run
Simply run the script:
```bash
python universal_runner.py
```

On first run, it will ask if you want to install enhanced packages for a better experience:
- `questionary` - Interactive prompts
- `rich` - Colored output and progress bars
- `click` - CLI argument parsing

**You can choose to:**
- Install them (recommended) - Better UI and features
- Skip them - Script works in basic mode with limited formatting

---

## 🚀 Quick Start

### Interactive Mode (Recommended for Beginners)

Just run the script and follow the prompts:
```bash
python universal_runner.py
```

The script will guide you through:
1. Select target folder
2. Choose file pattern (*.csv, *.txt, etc.)
3. Enable/disable recursive search
4. Select script type or enter custom command
5. Configure execution options
6. Preview and confirm
7. Execute with real-time progress

### CLI Mode (For Automation)

```bash
python universal_runner.py --folder ./data --script "python process.py" --pattern "*.csv"
```

---

## 📖 Usage Examples

### Example 1: Simple File Processing

**Scenario**: You have a Python script that processes CSV files one at a time.

**Your script** (`process_csv.py`):
```python
import sys
import pandas as pd

# Script expects file path as argument
file_path = sys.argv[1]

df = pd.read_csv(file_path)
print(f"Processed {len(df)} rows from {file_path}")
# ... do your processing
```

**Using Universal Script Runner**:
```bash
# Interactive mode
python universal_runner.py

# CLI mode
python universal_runner.py \
    --folder ./my_data \
    --script "python process_csv.py" \
    --pattern "*.csv" \
    --recursive
```

**Output**:
```
Found 5 file(s)

Processing files...
  ✅ data1.csv
  ✅ data2.csv
  ✅ data3.csv
  ✅ data4.csv
  ✅ data5.csv

📊 Execution Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status        Count    Percentage
─────────────────────────────────────
Total Files   5        100%
Successful    5        100.0%
Failed        0        0.0%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Example 2: Script with Custom Arguments

**Scenario**: Your script needs specific flags and arguments.

**Your script** (`analyze.py`):
```python
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file_path', help='Input file')
parser.add_argument('--mode', default='normal', help='Processing mode')
parser.add_argument('--output', help='Output directory')
args = parser.parse_args()

print(f"Analyzing {args.file_path} in {args.mode} mode")
# ... your analysis logic
```

**Using the {FILE} Placeholder**:

In interactive mode, when asked "Does your script need additional arguments?", say **Yes**, then enter:
```
python analyze.py --mode=strict {FILE} --output=./results
```

Or in CLI mode:
```bash
python universal_runner.py \
    --folder ./datasets \
    --script "python analyze.py --mode=strict {FILE} --output=./results" \
    --pattern "*.json"
```

**Why use {FILE}?**
- Allows you to position the file path **anywhere** in your command
- Supports complex argument structures
- More flexible than appending at the end

---

### Example 3: Node.js Script

**Your script** (`processor.js`):
```javascript
const fs = require('fs');

// Get file path from command line
const filePath = process.argv[2];

const data = fs.readFileSync(filePath, 'utf8');
console.log(`Processing: ${filePath}`);
// ... your processing logic
```

**Using Universal Script Runner**:
```bash
# Interactive mode - select "Node.js script" option
python universal_runner.py

# CLI mode
python universal_runner.py \
    --folder ./data \
    --script "node processor.js" \
    --pattern "*.json"
```

---

### Example 4: Shell Script (Linux/Mac)

**Your script** (`backup.sh`):
```bash
#!/bin/bash

FILE=$1
BACKUP_DIR="./backups"

echo "Backing up: $FILE"
cp "$FILE" "$BACKUP_DIR/$(basename $FILE).bak"
echo "Backup complete!"
```

**Using Universal Script Runner**:
```bash
python universal_runner.py \
    --folder ./documents \
    --script "bash backup.sh" \
    --pattern "*.txt" \
    --recursive
```

---

### Example 5: PowerShell Script (Windows)

**Your script** (`convert.ps1`):
```powershell
param($FilePath)

Write-Host "Converting: $FilePath"
# ... your conversion logic
Write-Host "Done!"
```

**Using Universal Script Runner**:
```bash
python universal_runner.py \
    --folder C:\Data \
    --script "powershell -File convert.ps1" \
    --pattern "*.csv"
```

---

### Example 6: Handling Interactive Scripts ⚠️

**Scenario**: Your script asks for user input.

**Your script** (`interactive_process.py`):
```python
import sys

file_path = sys.argv[1]

# This makes the script interactive!
user_name = input("Enter your name: ")
confirm = input(f"Process {file_path}? (y/n): ")

if confirm.lower() == 'y':
    print(f"Processing by {user_name}...")
    # ... processing logic
```

**What Happens**:
1. Universal Script Runner **detects** the `input()` calls
2. Shows a **warning panel** explaining the issue
3. Offers options:
   - **Cancel and modify script** (Recommended)
   - Use **pass-through mode** (you can interact, but no progress tracking)
   - Use **interactive mode** (one file at a time with pauses)

**Better Approach** (Recommended):
```python
import sys

file_path = sys.argv[1]
user_name = sys.argv[2] if len(sys.argv) > 2 else "Unknown"

print(f"Processing {file_path} by {user_name}...")
# ... processing logic
```

Then run:
```bash
python universal_runner.py \
    --folder ./data \
    --script "python interactive_process.py {FILE} John" \
    --pattern "*.csv"
```

---

## 🎛️ Execution Modes

### Capture Mode (Default)
- **Best for**: Non-interactive scripts
- **Features**: Progress bars, output capture, summary statistics
- **Use when**: Your script doesn't need user input

```bash
python universal_runner.py --folder ./data --script "python script.py" --mode capture
```

### Pass-Through Mode
- **Best for**: Interactive scripts, real-time output
- **Features**: Direct terminal access, real-time interaction
- **Limitations**: No progress tracking, no output capture

```bash
python universal_runner.py --folder ./data --script "python script.py" --mode passthrough
```

### Interactive Mode
- **Best for**: Scripts needing different input per file
- **Features**: Process one file at a time with pauses
- **Use when**: You need to review output between files

```bash
python universal_runner.py --folder ./data --script "python script.py" --mode interactive
```

---

## 🔧 Command Line Options

```bash
python universal_runner.py [OPTIONS]
```

### Options:

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--folder` | `-f` | Target folder path | Required |
| `--script` | `-s` | Script command to run | Required |
| `--pattern` | `-p` | File pattern (e.g., *.csv) | `*.csv` |
| `--recursive` | `-r` | Search in subfolders | `False` |
| `--show-output` | | Show script output (first 5 lines) | `False` |
| `--mode` | `-m` | Execution mode (capture/passthrough/interactive) | `capture` |

### Examples:

**Basic usage**:
```bash
python universal_runner.py -f ./data -s "python process.py" -p "*.csv"
```

**Recursive search with output**:
```bash
python universal_runner.py \
    --folder ./documents \
    --script "python analyze.py" \
    --pattern "*.txt" \
    --recursive \
    --show-output
```

**With custom arguments**:
```bash
python universal_runner.py \
    -f ./data \
    -s "python script.py --verbose {FILE} --output=results" \
    -p "*.json"
```

**Interactive mode**:
```bash
python universal_runner.py \
    -f ./data \
    -s "python interactive_script.py" \
    -m passthrough
```

---

## 💡 Best Practices

### 1. Design Scripts for Batch Processing

**❌ Don't do this**:
```python
filename = input("Enter filename: ")
data = process(filename)
```

**✅ Do this instead**:
```python
import sys
filename = sys.argv[1]
data = process(filename)
```

### 2. Use Argument Parsing

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('file_path', help='Input file')
parser.add_argument('--verbose', action='store_true', help='Verbose output')
parser.add_argument('--output', default='./output', help='Output directory')

args = parser.parse_args()

# Use args.file_path, args.verbose, args.output
```

### 3. Handle Errors Gracefully

```python
import sys

try:
    file_path = sys.argv[1]
    # ... your processing
    print(f"✅ Successfully processed: {file_path}")
except Exception as e:
    print(f"❌ Error processing {file_path}: {e}", file=sys.stderr)
    sys.exit(1)  # Exit with error code
```

### 4. Provide Progress Feedback

```python
import sys

file_path = sys.argv[1]

print(f"Starting processing: {file_path}")
# ... step 1
print("  Step 1: Loading data...")
# ... step 2
print("  Step 2: Processing...")
# ... step 3
print("  Step 3: Saving results...")
print(f"✅ Completed: {file_path}")
```

---

## 🧹 Cleanup

After using the script, you can remove the installed dependencies:

1. Complete your task
2. At the end, the script will ask: "Would you like to uninstall these packages now?"
3. Choose **Yes** to remove the packages and free up space (~2-5 MB)

**What happens**:
- Packages are removed from your system
- Next time you run the script, it will use **basic mode**
- The script still works, just with simpler interface

**Manual cleanup**:
```bash
pip uninstall questionary rich click -y
```

---

## 🐛 Troubleshooting

### Issue: "No files found matching the pattern"
**Solution**: Check your file pattern and folder path
```bash
# Make sure pattern includes asterisk
--pattern "*.csv"  # ✅ Correct
--pattern ".csv"   # ❌ Wrong
```

### Issue: Script hangs or freezes
**Possible causes**:
1. Your script is interactive (uses `input()`)
   - **Solution**: Use `--mode passthrough` or modify script
2. Script has infinite loop
   - **Solution**: Fix your script logic
3. Processing takes long time
   - **Solution**: Be patient or add timeout

### Issue: "Permission denied" error
**Solution**: 
- **Linux/Mac**: Make script executable: `chmod +x your_script.sh`
- **Windows**: Run as administrator if needed

### Issue: Module not found in my script
**Solution**: Install required packages for your script:
```bash
pip install pandas numpy requests  # or whatever your script needs
```

---

## 📝 Real-World Use Cases

### Data Processing Pipeline
Process hundreds of CSV files with data cleaning script:
```bash
python universal_runner.py \
    --folder ./raw_data \
    --script "python clean_data.py {FILE}" \
    --pattern "*.csv" \
    --recursive \
    --show-output
```

### Image Batch Processing
Resize all images in a folder:
```bash
python universal_runner.py \
    --folder ./images \
    --script "python resize_image.py {FILE} --width=800" \
    --pattern "*.jpg"
```

### Log File Analysis
Analyze log files and generate reports:
```bash
python universal_runner.py \
    --folder ./logs \
    --script "python analyze_logs.py {FILE} --output=./reports" \
    --pattern "*.log" \
    --recursive
```

### Code Format/Lint
Run linter on all Python files:
```bash
python universal_runner.py \
    --folder ./src \
    --script "python -m black {FILE}" \
    --pattern "*.py" \
    --recursive
```

### Database Import
Import multiple CSV files into database:
```bash
python universal_runner.py \
    --folder ./import_data \
    --script "python db_import.py {FILE} --table=users" \
    --pattern "*.csv"
```

---

## 🤝 Contributing

Feel free to enhance this script! Some ideas:
- Add support for parallel processing
- Save/load configuration presets
- Add logging to file
- Create progress reports
- Add dry-run mode

---

## 📄 License

This script is free to use and modify for your needs.

---

## 🆘 Support

If you encounter issues:
1. Check the Troubleshooting section
2. Verify your script works independently first
3. Try basic mode: decline package installation on first run
4. Check that file paths and patterns are correct

---

## 🎓 Learning Resources

**For Python beginners**:
- Learn about `sys.argv`: [Python Command Line Arguments](https://docs.python.org/3/library/sys.html#sys.argv)
- Learn about `argparse`: [Python Argument Parser](https://docs.python.org/3/library/argparse.html)

**For shell scripting**:
- Bash scripting: [Bash Guide](https://www.gnu.org/software/bash/manual/)
- PowerShell: [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)

---

## 🎯 Quick Reference Card

```bash
# Run in interactive mode (easiest)
python universal_runner.py

# Simple batch processing
python universal_runner.py -f FOLDER -s "python script.py" -p "*.csv"

# With custom arguments
python universal_runner.py -f FOLDER -s "python script.py --flag {FILE}" -p "*.txt"

# Recursive search
python universal_runner.py -f FOLDER -s "python script.py" -p "*.json" -r

# Show output
python universal_runner.py -f FOLDER -s "python script.py" --show-output

# Interactive scripts (pass-through)
python universal_runner.py -f FOLDER -s "python script.py" -m passthrough

# Cleanup packages
# (prompted at end of execution, or manual: pip uninstall questionary rich click -y)
```

---

**Happy scripting! 🚀**