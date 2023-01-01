from ortools.sat.python import cp_model


def ortools_sechedule(
        lst_employees: list = [],
        day_of_this_month: int = 30,
        max_employee_one_shifts: int = 3,
        min_employee_one_shifts: int = 2,
        max_continue_shifts: int = 7,
        lst_leave: list = []
):
    # 定義模型
    model = cp_model.CpModel()

    # 定義變量
    # 員工們的名字
    employees = lst_employees

    # 每個員工在每一天的排班狀態，0表示不工作，1表示工作
    schedules = {}
    for employee in employees:
        schedules[employee] = {}
        for day in range(1, day_of_this_month + 1):
            schedules[employee][day] = model.NewBoolVar(f"{employee}_{day}")

    # 定義限制
    # 每週工作5天休息2天
    for week in range(1, 5):
        for employee in employees:
            model.Add(sum(schedules[employee][day] for day in range((week - 1) * 7 + 1, week * 7 + 1)) == 5)

    # 一班最少兩人最多三人
    for day in range(1, 31):
        model.Add(sum(schedules[employee][day] for employee in employees) >= min_employee_one_shifts)
        model.Add(sum(schedules[employee][day] for employee in employees) <= max_employee_one_shifts)

    # 最大平均員工上班天數
    model.Add(sum(sum(schedules[employee][day] for day in range(1, day_of_this_month + 1)) for employee in
                  employees) <= day_of_this_month * len(employees))

    # 不能連續上班7天
    for employee in employees:
        for day in range(1, 25):
            model.Add(
                sum(schedules[employee][day + i] for i in range(max_continue_shifts)) <= (max_continue_shifts - 1))

    # lst_leave = [['a',1],['a',2],['a',3]]
    for i in lst_leave:
        model.Add(schedules[i[0]][i[1]] == 0)

    # a 1 3 15 20休息
    # model.Add(schedules["a"][1] == 0)
    # model.Add(schedules["a"][3] == 0)
    # model.Add(schedules["a"][15] == 0)
    # model.Add(schedules["a"][20] == 0)

    # 啟動求解器
    solver = cp_model.CpSolver()

    # 設定求解器參數
    solver.parameters.max_time_in_seconds = 30

    # 執行求解
    status = solver.Solve(model)

    # 輸出結果
    lst_output = []
    if status == cp_model.OPTIMAL:
        for employee in employees:
            print(f"{employee}: ", end="")
            lst_shifts = []
            for day in range(1, 31):
                if solver.Value(schedules[employee][day]) == 1:
                    print(f"{day} ", end="")
                    lst_shifts.append(day)
            dic_output = {
                employee: lst_shifts
            }
            lst_output.append(dic_output)
            print()
    else:
        print("無解")

    return lst_output
