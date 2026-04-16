#!/usr/bin/env python3
"""
One-Click Ollama Setup for Invoice Verification Agent
This script helps you pull a local Ollama model and configure the app to use it.
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and report status."""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ Success!")
            return True
        else:
            print(f"❌ Failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout - operation took too long")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_config(model_name):
    """Update MODEL_TO_USE in invoice_verification_agent.py"""
    print(f"\n📝 Updating configuration...")
    
    config_file = "invoice_verification_agent.py"
    if not os.path.exists(config_file):
        print(f"❌ File not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the MODEL_TO_USE value
        old_line = 'MODEL_TO_USE = "gemma4:31b-cloud"'
        new_line = f'MODEL_TO_USE = "{model_name}"'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated MODEL_TO_USE to: {model_name}")
            return True
        else:
            print(f"⚠️ Could not find configuration line to update")
            print(f"   Looking for: {old_line}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("🎉 Ollama Setup - Invoice Verification Agent")
    print("=" * 70)
    
    models = [
        ("1", "gemma2", "2.6GB - Recommended (fast & good quality)"),
        ("2", "mistral", "4.1GB - Excellent quality"),
        ("3", "neural-chat", "4GB - Very good for conversations"),
        ("4", "llama2", "3.8GB - Popular and balanced"),
        ("5", "skip", "Skip pulling (use mock data only)"),
    ]
    
    print("\n📚 Available Models:")
    for num, model, desc in models:
        print(f"{num}. {model:15} - {desc}")
    
    print("\n🔧 Which model would you like to use?")
    choice = input("Enter number (1-5): ").strip()
    
    if choice not in ["1", "2", "3", "4", "5"]:
        print("❌ Invalid choice")
        return False
    
    if choice == "5":
        print("\n✅ Skipping model setup - app will use mock data")
        print("   (This is fine for testing)")
        return True
    
    model_info = [m for m in models if m[0] == choice][0]
    model_name = model_info[1]
    
    print(f"\n📥 Pulling {model_name}...")
    print("   (This may take 5-15 minutes depending on your internet speed)")
    
    if run_command(f"ollama pull {model_name}", f"Pulling {model_name}"):
        if update_config(model_name):
            print("\n" + "=" * 70)
            print("✅ SETUP COMPLETE!")
            print("=" * 70)
            print(f"\n✓ Model: {model_name} is ready")
            print(f"✓ Configuration updated")
            print("\n🚀 Next steps:")
            print("   1. Start Streamlit: streamlit run app.py")
            print("   2. Upload an invoice file")
            print("   3. Watch the LLM extract real data instead of mock data!")
            print("\n💡 Tips:")
            print("   • First run might be slow as model loads into memory")
            print("   • Subsequent runs will be faster")
            print("   • To test: python invoice_verification_agent.py")
            print("\n" + "=" * 70)
            return True
        else:
            print("❌ Failed to update configuration")
            print(f"   Please manually update MODEL_TO_USE to '{model_name}'")
            return False
    else:
        print("❌ Failed to pull model")
        print("   Possible causes:")
        print("   • Ollama not installed - download from https://ollama.ai")
        print("   • Internet connection issues")
        print("   • Insufficient disk space")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
