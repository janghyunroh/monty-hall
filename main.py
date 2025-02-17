import curses
import random
from wcwidth import wcswidth  # 실제 화면상의 너비 계산용

def simulate_monty_hall(simulations, total_doors, open_doors, switch):
    wins = 0
    losses = 0
    for _ in range(simulations):
        # 자동차가 숨겨진 문의 번호 (0 ~ total_doors-1)
        car = random.randint(0, total_doors - 1)
        # 참가자의 초기 선택
        chosen = random.randint(0, total_doors - 1)
        
        # 몬티가 열 수 있는 문의 목록 결정
        if chosen == car:
            available = [d for d in range(total_doors) if d != chosen]
        else:
            available = [d for d in range(total_doors) if d != chosen and d != car]
        
        # available 목록에서 open_doors 개수를 랜덤 선택
        opened = random.sample(available, open_doors)
        # 남은 문의 목록 (열리지 않은 문)
        remaining = [d for d in range(total_doors) if d not in opened]
        
        # 선택 변경 시: 원래 선택한 문을 제외한 문 중 하나로 변경
        if switch:
            new_choices = [d for d in remaining if d != chosen]
            final_choice = random.choice(new_choices)
        else:
            final_choice = chosen
        
        if final_choice == car:
            wins += 1
        else:
            losses += 1
    return wins, losses

def choose_option(stdscr, row, prompt, options):
    """
    한 줄에 prompt와 옵션을 출력하고, 방향키로 선택 후 엔터키를 누르면 선택한 옵션을 반환.
    (이 함수에서는 커서를 프롬프트 끝으로 이동시키지 않고, 한 줄 전체를 다시 그립니다.)
    """
    selected = 0
    while True:
        stdscr.move(row, 0)
        stdscr.clrtoeol()
        stdscr.addstr(row, 0, prompt)
        # 프롬프트 출력 후 한 칸 띄운 후 옵션 출력
        base_col = wcswidth(prompt) + 1  
        temp_col = base_col
        for idx, option in enumerate(options):
            text = f" {option} "
            if idx == selected:
                stdscr.addstr(row, temp_col, text, curses.A_REVERSE)
            else:
                stdscr.addstr(row, temp_col, text)
            temp_col += wcswidth(text)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [curses.KEY_LEFT, curses.KEY_UP]:
            selected = (selected - 1) % len(options)
        elif key in [curses.KEY_RIGHT, curses.KEY_DOWN]:
            selected = (selected + 1) % len(options)
        elif key in [10, 13]:
            return options[selected]

def main(stdscr):
    row = 0
    curses.curs_set(1)  # 텍스트 입력 시 커서 표시

    while True:
        # 1. 시뮬레이션 횟수 입력
        prompt_sim = "시뮬레이션 횟수를 입력하세요: "
        stdscr.addstr(row, 0, prompt_sim)
        stdscr.refresh()
        curses.echo()
        # 텍스트 입력은 프롬프트 끝으로 커서 이동
        stdscr.move(row, wcswidth(prompt_sim))
        sim_str = stdscr.getstr().decode().strip()
        curses.noecho()
        row += 1
        try:
            simulations = int(sim_str)
        except ValueError:
            stdscr.addstr(row, 0, "유효한 정수를 입력하세요.\n")
            row += 1
            continue

        # 2. 몬티홀 쇼의 문 개수 입력 (문 개수는 최소 3개여야 함)
        valid_total_doors = False
        while not valid_total_doors:
            prompt_doors = "몬티홀 쇼의 문 개수를 입력하세요 (최소 3개): "
            stdscr.addstr(row, 0, prompt_doors)
            stdscr.refresh()
            curses.echo()
            stdscr.move(row, wcswidth(prompt_doors))
            door_str = stdscr.getstr().decode().strip()
            curses.noecho()
            row += 1
            try:
                total_doors = int(door_str)
                if total_doors < 3:
                    stdscr.addstr(row, 0, "문의 개수는 최소 3개여야 합니다.\n")
                    row += 1
                else:
                    valid_total_doors = True
            except ValueError:
                stdscr.addstr(row, 0, "유효한 정수를 입력하세요.\n")
                row += 1

        # 3. 몬티가 열 문의 개수 입력 (전체 문보다 최소 2 작아야 함)
        prompt_open = "몬티가 열 문의 개수를 입력하세요(위 숫자보다 적어도 2만큼 작아야 합니다): "
        stdscr.addstr(row, 0, prompt_open)
        stdscr.refresh()
        curses.echo()
        stdscr.move(row, wcswidth(prompt_open))
        open_str = stdscr.getstr().decode().strip()
        curses.noecho()
        row += 1
        try:
            open_doors = int(open_str)
        except ValueError:
            stdscr.addstr(row, 0, "유효한 정수를 입력하세요.\n")
            row += 1
            continue
        if open_doors > total_doors - 2:
            stdscr.addstr(row, 0, "열 문의 개수는 전체 문의 개수보다 최소 2 작아야 합니다.\n")
            row += 1
            continue

        # 4. 문이 열렸을 때 선택 변경 여부 (예 / 아니오)
        switch_prompt = "문이 열렸을 때 선택을 바꿀지 말지 고르세요: "
        switch_choice = choose_option(stdscr, row, switch_prompt, ["예", "아니오"])
        row += 1
        switch = True if switch_choice == "예" else False

        # 시뮬레이션 실행
        wins, losses = simulate_monty_hall(simulations, total_doors, open_doors, switch)
        result_str = f"결과: 자동차 당첨 {wins}회, 미당첨 {losses}회\n"
        stdscr.addstr(row, 0, result_str)
        row += 1

        # 5. 프로그램 재실행 여부 (예 / 아니오)
        again_prompt = "다시 할 건지 고르세요: "
        again_choice = choose_option(stdscr, row, again_prompt, ["예", "아니오"])
        row += 1
        if again_choice == "아니오":
            break

        stdscr.addstr(row, 0, "-" * 50 + "\n")
        row += 1

    stdscr.addstr(row, 0, "프로그램을 종료합니다. 아무 키나 누르세요.")
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
