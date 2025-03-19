"""
A personalized daily planner function that helps the users to list their tasks

@param name: a string represents users name
@return: a string contains the formated daily planner
"""
def daily_planner(name):
    print('\n\t\033[94m[Create your own daily planner]\033[0m')
    tdlist = []

    # store the task and priority in 'tdlist'
    while True:
        task = input('\n\t\033[94mEnter your task (type \'done\' to finish): \033[0m\n\t>> ').strip()
        if task.lower() == 'done':
            break

        priority = input('\n\t\033[94mPriority (from 1 to 3, 1 is the highest priority): \033[0m\n\t>> ').strip()
        if priority not in ['1', '2', '3']:
            print('\t⚠️ \033[93mInvalid input. Please enter 1, 2, or 3.\033[0m')
            priority = input('\n\t\033[94mPriority (from 1 to 3, 1 is the highest priority): \033[0m\n\t>> ').strip()

        tdlist.append({'task':task, 'priority':priority})

    # sort 'tdlist' according to the priority
    sorted_tdlist = sorted(tdlist, key=lambda x: x['priority'])

    # change the priority from number to text
    for i in sorted_tdlist:
        if i['priority'] == '1':
            i['priority'] = '[HIGH]'
        elif i['priority'] == '2':
            i['priority'] = '[MEDIUM]'
        else:
            i['priority'] = '[LOW]'
    
    # print the result
    result = ''
    result += f'\n\t\033[92m~~~~~{name}\'s schedule for today~~~~~\n'
    for i in range(len(sorted_tdlist)):
        task = sorted_tdlist[i]
        result += f"\t{i+1}. {task['priority'].ljust(9)} {task['task']}\n"
    result += '\033[0m'

    return result