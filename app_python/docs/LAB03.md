
## Почему Pytest а не unittest?

Для работы я выбрал pytest, потому что его удобно использовать используя оператор assert без необходимости писать сложные конструкции.
## Тесты

test_main - проверка корневого запроса, статус код 200 и ключей в ответе

test_health - проверка статус кода 200 и status = healthy 

test_unknown - проверка работоспособности обработчика ошибок


## Выводы команд

```console
…/DevOps-Core-Course/app_python master *?↑ ❯ pytest   
...                                                                                                                                            [100%]
3 passed in 0.32s
```

```console 
…/DevOps-Core-Course/app_python master *?↑ ❯ ruff check .                        
All checks passed!
```



