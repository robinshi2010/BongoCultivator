from src.cultivator import Cultivator

def main():
    print("=== Plan 5 Verification ===")
    
    # Mock Cultivator
    c = Cultivator()
    
    # 1. Test "whosyourdaddy" (Target: 1)
    c.layer_index = 0 # 炼气
    print(f"\n[Test 1] whosyourdaddy (Current: {c.layer_index})")
    success, msg = c.process_secret_command("whosyourdaddy")
    print(f"Result: {success}, Msg: {msg}")
    if success and c.layer_index == 1:
        print("PASS: Upgraded to Tier 1")
    else:
        print("FAIL")

    # Repeat test (Should fail)
    print(f"\n[Test 2] whosyourdaddy (Current: {c.layer_index} - Already Tier 1)")
    success, msg = c.process_secret_command("whosyourdaddy")
    print(f"Result: {success}, Msg: {msg}")
    if not success:
        print("PASS: Correctly rejected")
    else:
        print("FAIL: Allow upgrade from wrong tier")

    # 2. Test "上上下下左左右右baba" (Target: 2)
    # Current is 1
    print(f"\n[Test 3] Konami Code (Current: {c.layer_index})")
    success, msg = c.process_secret_command("上上下下左左右右baba")
    print(f"Result: {success}, Msg: {msg}")
    if success and c.layer_index == 2:
        print("PASS: Upgraded to Tier 2")
    else:
        print("FAIL")
        
    # 3. Test "haiwangshabi" (Target: 3)
    # Current is 2
    print(f"\n[Test 4] Haiwang Code (Current: {c.layer_index})")
    success, msg = c.process_secret_command("haiwangshabi")
    print(f"Result: {success}, Msg: {msg}")
    if success and c.layer_index == 3:
        print("PASS: Upgraded to Tier 3")
    else:
        print("FAIL")

    # 4. Invalid Code
    print(f"\n[Test 5] Invalid Code")
    success, _ = c.process_secret_command("showmethemoney")
    if not success:
        print("PASS: Invalid code rejected")
    else:
        print("FAIL")

if __name__ == "__main__":
    main()
