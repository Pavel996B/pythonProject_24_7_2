from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password, empty_email, empty_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбоскин', animal_type='двортерьер',
                                     age="4", pet_photo='images/cat1.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", 3, "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("Питомцы отсутствуют")


# 10 тестов для API PetFriends
def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    """ТЕСТ-1. Проверяем что запрос api ключа возвращает статус 403 при передаче несуществующего юзера"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


def test_get_api_key_with_empty_user_data(email=empty_email, password=empty_password):
    """ТЕСТ-2. Проверка того, что запрос API-ключа c пустыми значениями логина и пароля пользователя возвращает статус '403'
    и что результат не содержит слово 'key'"""

    # Отправка запроса и сохранение полученного ответа с кодом статуса в 'status', а текста ответа - в 'result'
    status, result = pf.get_api_key(email, password)

    # Сопоставление полученных данных с ожидаемым результатом
    assert status == 403
    assert 'key' not in result


def test_add_new_pet_without_photo_with_valid_data(name='Зик', animal_type='Попугай', age=2):
    """ТЕСТ-3. Проверка возможности добавления питомца без фото с корректными данными"""

    # Запрос API-ключа
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавление нового питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сопоставление полученных данных с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_without_photo_and_with_empty_data(name='', animal_type='', age=''):
    """ТЕСТ-4. Проверка невозможности добавления питомца без фото и с незаполненными данными """
    """Баг"""

    # Запрос API-ключа
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавление нового питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сопоставление полученных данных с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_with_photo_and_empty_data(name='', animal_type='', age='', pet_photo='images/cat1.jpg'):
    """ТЕСТ-5. Проверка невозможности добавления питомца с фото и незаполненными данными """
    """Баг"""

    # Запрос API-ключа
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Получение полного пути изображения питомца и его сохранение в переменную 'pet_photo'
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Добавление нового питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сопоставление полученных данных с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_with_invalid_age(name='Барбоскин', animal_type='двортерьер',
                                     age='cnuer'):
    """ТЕСТ-6. Проверяем что нельзя добавить питомца с некорректными данными"""
    """Баг"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


def test_successful_add_self_pet_photo(pet_photo='images/P1040103.jpg'):
    """ТЕСТ-7. Проверяем возможность добавления фото для питомца"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, api_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

    # Проверяем, есть ли питомцы в списке
    if len(my_pets['pets']) > 0:
        # Получаем идентификатор первого питомца
        pet_id = my_pets['pets'][0]['id']

        # Добавляем фотографию питомца
        status, result = pf.add_pet_photo(api_key, pet_id, pet_photo)

        # Получаем обновленный список питомцев
        _, my_pets = pf.get_list_of_pets(api_key, 'my_pets')

        # Проверяем статус ответа и соответствие фотографии питомца
        assert status == 200
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
    else:
        # Если список питомцев пустой, всплывает исключение с текстом об отсутствии питомцев
        raise Exception("Питомцы отсутствуют")


def test_add_new_pet_with_incorrect_age(name='Мурка', animal_type='Кошка',
                                        age='-5', pet_photo='images/cat1.jpg'):
    """ТЕСТ-8. Проверка невозможности добавления питомца с отрицательным возрастом"""
    """Баг"""

    # Запрос API-ключа
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Получение полного пути изображения питомца и его сохранение в переменную 'pet_photo'
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Добавление нового питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сопоставление полученных данных с ожидаемым результатом
    assert status == 200
    assert result['age'] == age


def test_delete_not_own_pet():
    """ТЕСТ-9. Проверка невозможности удаления 'не своего питомца'"""
    """Баг"""

    # Запрос API-ключа и списка всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key, '')

    # Если список не пустой, происходит отправка запроса на удаление первого питомца
    if len(all_pets['pets']) > 0:
        pet_id = all_pets['pets'][0]['id']
        status = pf.delete_pet(auth_key, pet_id)

        # Сопоставление полученных данных с ожидаемым результатом
        assert status == 200
        assert pet_id not in all_pets.values()
    else:
        # Если список питомцев пустой, всплывает исключение с текстом об отсутствии питомцев
        raise Exception('There is no pets')


def test_set_photo_not_own_pet(pet_photo="images/P1040103.jpg"):
    """Проверка возможности добавления фото к информации о 'не своем питомце'"""

    # Запрос API-ключа и списка всех питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key, '')

    # Если список не пустой, происходит добавление фото
    if len(all_pets['pets']) > 0:
        pet_id = all_pets['pets'][0]['id']
        status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)

        # Сопоставление полученных данных с ожидаемым результатом
        assert status == 500
    else:
        # Если список питомцев пустой, всплывает исключение с текстом об отсутствии питомцев
        raise Exception('Питомцы отсутствуют')