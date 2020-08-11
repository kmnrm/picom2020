# picom летняя кухня 2020-7

Бэкенд веб-приложения с заведениями китайского города.

*Заведения имеют следующие атрибуты:*
- название (обязательное поле)
- владелец
- категория (бар, клуб, кафе, паб) (обязательное поле)
- рейтинг безопасности от 1 до 5 (police rating)
- описание
- адрес на китайском (обязательное поле)
- адрес на пиньине (рассчитывается автоматически)
- режим работы
- средняя стоимость напитков/блюд (рассчитывается автоматически как mean)
- кординаты - широта и долгота (рассчитываются автоматически через геокодер)
- фотографии (представлены отдельной моделью)
- отзывы
- рейтинг (рассчитывается как среднее арифметическое имеющихся оценок отзывов)
- события (events, Events model related name)

*Свойства инстанса события:*
- название
- заведение, в котором оно проводится (foreign key Place)
- описание
- стоимость на входе
- фото афиши
- дата и время

*Атрибуты напитка:*
- название
- цена
- место, в котором его наливают 

*Атрибуты отзыва:*
- автор отзыва
- место, на которое оставлен отзыв
- текст отзыва
- оценка (необязательное поле, в таком случае оценка 0)
- дата публикации отзыва

##### Права доступа
При регистрации пользователь автоматически попадает в группу "Users". Чтобы создать заведение пользователь должен находиться в группе "Owners"(владелец). Заведения может создавать и редактировать только владелец, напитки и события добавлять и редактировать может только создатель заведения.


#### Запуск
```bash
picom$ python manage.py migrate
picom$ python manage.py runserver
```

#### Модели:
- Place
- Place Image
- Event
- Place Review
- Drink

#### Примеры API endpoints

1. Place List (GET)
![place_list](screenshots/api_place_list.png)

2. Place Instnace (GET)
![place_instance](screenshots/api_get_place.png)

3. Events List (GET)
![events_list](screenshots/api_event_list.png)

4. Drink Instance (GET)
![drink_instnace](screenshots/api_get_drink.png)

5. User Registration (POST)
![new_user](screenshots/api_new_user.png)
![new_user_created](screenshots/api_new_user_201.png)

6. User Authorization (POST)
![user_login](screenshots/api_user_login.png)


#### Пример админки

Place Admin
![place_admin](screenshots/admin_place.png)
