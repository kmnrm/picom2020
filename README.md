# picom летняя кухня 2020-7

Веб-приложение с заведениями китайского города.

[Here we go!](https://kmnrm2.pythonanywhere.com)

### Backend

[Swagger specifications](https://kmnrm2.pythonanywhere.com/api/swagger/)

*Заведения имеют следующие атрибуты:*
- название (обязательное поле)
- владелец
- категория (бар, клуб, кафе, паб) (обязательное поле)
- рейтинг безопасности от 1 до 5 (police rating)
- описание
- адрес на китайском (обязательное поле)
- адрес на пиньине (рассчитывается автоматически)
- логотип заведения (изображение размером 100х100)
- номер телефона (с валидацией; формат - CN national)
- режим работы
- средняя стоимость напитков/блюд (рассчитывается автоматически как mean)
- кординаты - широта и долгота (рассчитываются автоматически через геокодер)
- фотографии (представлены отдельной моделью)
- отзывы
- рейтинг (рассчитывается как среднее арифметическое имеющихся оценок отзывов)
- события (events, Events model related name)
- напитки (drinks, Drink model related name)

*Атрибуты события:*
- название
- заведение, в котором оно проводится (foreign key Place)
- описание
- стоимость на входе
- фото афиши
- дата события
- время начала события
- время окончания события

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

##### Фильтрация
Реализована фильтрация `places-list` по названию заведения (`title__contains`).
```shell script
http://hostname/api/places?title=space
```


#### Модели:
- Place
- Place Image
- Event
- Place Review
- Drink


#### Пример админки

#### Place Admin

Структура:
- Main info
- Additional info
- Images
- Events

 **Main info**

![place_admin_main_info](screenshots/admin_place_main_info.png)


**Additional info and images**

![place_admin_main_info](screenshots/admin_place_add_info_imgs.png)

**Events**

![place_admin_main_info](screenshots/admin_place_events.png)

Данные из базы данных передаются на фронтенд [в формате `geoJSON`](place.json).



#### Запуск
Для корректной работы сервера на локальной машине необходим `.env` файл со следующими переменными окружения:

```env
BAIDUV3_GEOCODER_KEY=здесь_будет_ваш_baidu_api_key
BAIDU_SECURITY_KEY=здесь_будет_ваш_security_key
SECRET_KEY=здесь_будет_ваш_project_secret_key
DEBUG=True
```
Также для построения маршрута необходим API-ключ [Mapbox](https://docs.mapbox.com/api/), который необходимо сохранить в файле `config.js` в `static/js`:
```JavaScript
var config = {
  MAPBOX_KEY : 'ВАШ_API_KEY'
}
```

##### Команды для запуска 
```bash
picom$ pip3 install -r requirements.txt
picom$ python3 manage.py migrate
picom$ python3 manage.py runserver
```
