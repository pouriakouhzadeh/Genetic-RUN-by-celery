import random
import pandas as pd
from celery import group
from tasks import train_model_task

currency_files = [
    "EURUSD60.csv", "AUDCAD60.csv", "AUDCHF60.csv",
    "AUDNZD60.csv", "AUDUSD60.csv", "EURAUD60.csv",
    "EURCHF60.csv", "EURGBP60.csv", "GBPUSD60.csv",
    "USDCAD60.csv", "USDCHF60.csv"
]

def read_data(file_name, tail_size=7000):
    try:
        data = pd.read_csv(file_name)
        return data.tail(tail_size)
    except FileNotFoundError:
        print(f"File {file_name} not found.")
        return None

def generate_individual(param_space):
    individual = [random.randint(param[0], param[1]) for param in param_space[:-1]]
    allowed_hours = random.sample(range(3, 24), random.randint(param_space[-1][0], param_space[-1][1]))
    individual.append(allowed_hours)
    return individual

def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 2)
    child = parent1[:crossover_point] + parent2[crossover_point:]
    child[-1] = sorted(list(set(child[-1])))  # Ensure unique allowed_hours
    return child

def mutate(individual, mutation_rate, param_space):
    for i in range(len(individual) - 1):
        if random.random() < mutation_rate:
            individual[i] = random.randint(param_space[i][0], param_space[i][1])
    # Mutate allowed_hours
    if random.random() < mutation_rate:
        new_hour = random.choice(list(set(range(3, 24)) - set(individual[-1])))
        individual[-1].append(new_hour)
        if len(individual[-1]) > param_space[-1][1]:  # Ensure within allowed_hours limit
            individual[-1].remove(random.choice(individual[-1]))
    return individual

def save_to_file(data, file_name="ga_results.txt"):
    with open(file_name, "a") as file:
        file.write(data + "\n")









def evaluate_population(population, currency_files):
    results = []  # نتایج برای هر فرد
    tasks = []
    fitness_scores = []  # اینجا یک لیست برای نگهداری امتیازات ایجاد می‌کنیم

    # حلقه بر روی جمعیت
    for individual in population:
        total_acc = 0
        valid_models = 0
        # حلقه بر روی فایل‌های ارز
        for currency_file in currency_files:
            currency_data = read_data(currency_file, 7000)
            if currency_data is not None:
                temp = currency_data.to_json(orient='split')
                # اطمینان حاصل کنید که individual به صورت مناسبی آرگومان‌ها را برای train_model_task فراهم می‌کند
                # فرض بر این است که individual[-1] حاوی 'allowed_hours' است و بقیه عناصر آرگومان‌های دیگر را شامل می‌شوند
                task = train_model_task.s(temp, *individual[:-1], individual[-1])
                tasks.append(task)


    job = group(tasks)()
    results = job.get()  # results حاوی نتایج بازگشتی از هر کار است

    for result in results:
        try:
            # فرض می‌شود که هر نتیجه به صورت یک تاپل از (acc, wins, loses) بازگردانده شده است
            acc, wins, loses = result
            # این قسمت باید بر اساس ساختار دقیق نتایج بازگشتی از تابع train_model_task شما تنظیم شود
            if wins + loses >= 0.2 * (individual[3] * 0.033):  # این شرط باید بر اساس لاجیک مورد نظر شما تنظیم شود
                total_acc += acc
                valid_models += 1
        except Exception as e:
            print(f"Error processing task: {e}")


            if valid_models > 0:
                avg_acc = total_acc / valid_models
            else:
                avg_acc = 0  # اگر مدل معتبری نباشد، دقت میانگین صفر در نظر گرفته می‌شود
            fitness_scores.append(avg_acc)  # اضافه کردن دقت میانگین هر فرد به لیست
    print("stage finish")
    return fitness_scores  # برگرداندن لیست امتیازات دقت برای هر فرد در جمعیت



def genetic_algorithm(currency_files, population_size, generations, mutation_rate, param_space):
    print("Genetic algoritm is start ...")
    population = [generate_individual(param_space) for _ in range(population_size)]
    for generation in range(generations):
        fitness_scores = evaluate_population(population, currency_files)
        population_fitness = list(zip(population, fitness_scores))
        population_fitness.sort(key=lambda x: x[1], reverse=True)
        
        # Selection
        selected = population_fitness[:len(population) // 2]
        population = [individual for individual, _ in selected]
        
        # Crossover and mutation
        while len(population) < population_size:
            if len(selected) >= 2:
                parent1, parent2 = random.sample(selected, 2)
            else:
                parent1 = generate_individual(param_space)
                parent2 = generate_individual(param_space)

            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate, param_space)
            population.append(child)
        try :
            best_individual, best_fitness = population_fitness[0]
            save_to_file(f"Generation {generation}: Best Fitness = {best_fitness}, best individual = {best_individual}")
        except :
            save_to_file(f"population fitness in empty")


param_space = [(2, 16), (2, 20), (30, 500), (500, 6000), (100, 5000), (52, 70), (8, 18)]  # Example param_space including allowed_hours range
genetic_algorithm(currency_files, 150, 40, 0.02, param_space)
