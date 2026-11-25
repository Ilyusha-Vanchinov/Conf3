; Инициализация исходного массива 100..105
load_const 10
load_const 100
store_mem 0

load_const 20
load_const 101
store_mem 0

load_const 30
load_const 102
store_mem 0

load_const 40
load_const 103
store_mem 0

load_const 50
load_const 104
store_mem 0

load_const 60
load_const 105
store_mem 0

; Копирование 100..105 -> 200..205
load_mem 100
load_const 200
store_mem 0

load_mem 101
load_const 201
store_mem 0

load_mem 102
load_const 202
store_mem 0

load_mem 103
load_const 203
store_mem 0

load_mem 104
load_const 204
store_mem 0

load_mem 105
load_const 205
store_mem 0