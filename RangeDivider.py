def create_intervals(start, end, num_intervals):
    interval_size = (end - start) // num_intervals
    intervals = [(start + i * interval_size, start + (i+1) * interval_size) for i in range(num_intervals)]
    return intervals

start = int(input("Введите начало диапазона в шестнадцатеричном формате: "), 16)
end = int(input("Введите конец диапазона в шестнадцатеричном формате: "), 16)
num_intervals = int(input("Введите количество интервалов: "))

intervals = create_intervals(start, end, num_intervals)

print("Список интервалов:")
for interval in intervals:
    print("{:x} {:x}".format(interval[0], interval[1]))