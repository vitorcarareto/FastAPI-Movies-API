import asyncio
import pytest
from starlette.testclient import TestClient
from starlette.status import *
from run import app, connect_db, disconnect_db
from utils.db import execute, fetch

client = TestClient(app)
loop = asyncio.get_event_loop()

username = "admin"
password = "123"
new_user_id, new_movie_id = None, None

@pytest.fixture(scope='session', autouse=True)
def db_conn():
    # Will be executed before the first test
    db = loop.run_until_complete(connect_db())
    yield db
    # Will be executed after the last test
    loop.run_until_complete(disconnect_db(db))


def db_delete_user(username):
    query = """ delete from users where username = :username; """
    loop.run_until_complete(execute(query, is_many=False, values={"username": username}))
    return


def login(username, password):
    response = client.post("/login", data={
        "username": username,
        "password": password,
    })
    return response

def get_auth_header(username, password):
    response = login(username, password)
    jwt_token = response.json()['access_token']
    auth_header = {"Authorization": f"Bearer {jwt_token}"}
    return auth_header


def test_login_successful():
    response = login(username, password)
    assert response.status_code == HTTP_200_OK
    assert "access_token" in response.json()


def test_login_unsuccessful():
    response = login(username, "wrong-password")
    assert response.status_code == HTTP_401_UNAUTHORIZED
    assert "access_token" not in response.json()


def test_post_user():
    user_dict = {
        "username": "test-user",
        "password": "test-password",
        "email": "test@email.com",
        "role": "personal"
    }
    # Delete user if exists
    db_delete_user(user_dict['username'])

    # Create user
    response = client.post("/v1/users", json=user_dict)
    assert response.status_code == HTTP_201_CREATED
    global new_user_id
    new_user_id = response.json().get('id')

    # Assert that user already exists
    response = client.post("/v1/users", json=user_dict)
    assert response.status_code == HTTP_400_BAD_REQUEST


def test_patch_user():
    auth_header = get_auth_header(username, password)
    patch_dict = {
        "value": "personal"
    }

    response = client.patch(f"/v1/users/{new_user_id}/role", json=patch_dict, headers=auth_header)
    assert response.status_code == HTTP_200_OK
    assert response.json()['role'] == patch_dict['value']


def test_get_user():
    auth_header = get_auth_header(username, password)
    response = client.get(f"/v1/users/{new_user_id}", headers=auth_header)
    assert response.status_code == HTTP_200_OK
    assert 'username' in response.json()


def test_post_movie():
    auth_header = get_auth_header(username, password)
    user_dict = {
        "title": "Test Movie!",
        "description": "Example movie complete description.",
        "stock": 3,
        "rental_price": 7.53,
        "sale_price": 28.60,
        "availability": True,
        "images": [
            "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAKAAawMBIgACEQEDEQH/xAAbAAACAgMBAAAAAAAAAAAAAAAFBgMEAQIHAP/EAD4QAAIBAwMBBgMGAwYGAwAAAAECAwAEEQUSITEGEyJBUWEUMnGBkaGxwdEjQvAHFSSS4fEWM0NSYrMlNHL/xAAZAQADAQEBAAAAAAAAAAAAAAACAwQBBQD/xAAiEQACAgICAQUBAAAAAAAAAAAAAQIRAyESMQQTIkFRYRT/2gAMAwEAAhEDEQA/AAEmknJ35QZwSfKhd1o8e5/8dHwpORtwcDoMsOT746/ZT32sv7TQojLcwbmbGxPOucvreoai05stPUovid8eGME4G49BzxzUmO3uiqeiFtKtzNMkuqW8QjYBXYcSDzI58qxdaPHEkKnUIWmeIEJGNwzkADOR65zjoD6UNuJZrhlE/wDDPow24zTRLY7J9EDnd30SAMAcEgkHr9lWY1ZDnnx2BDo9v3zJ/fFkcMwO05IA5Bx55548qkg0q0YybtZtAiqGUujKXzjjBxzz6noal1PT/gu3Utkwwm8sB7GPP71XuoQg6imRjdgOfX6Vb6Bbad44p0uEU8SJ0atbaNJpVSWZYUOcyMuQMAnp55xj7a0ll42gVGWG0AdaIJBM6XbNlBrNqoz8zeEHBx5nz5P3evELWdvuKtqlrsEYfd1L9cADyOFBIJ8wPrAttJIhlAOIkZm9hih8gbxEsOGIxSpdhroLf3RblgG1uxAyo4fIxkAnr5eI++B68ej020cbH1mBSE3A7RsPCkAHcOfERgjqrelR6RBaFhJdlmUclQcZo8msaJZJ/C0eM8Y37c8/X7DS+QziLt3apbuqW9zFdI2cPACRwSBkeR4/361GqSkD+DJ/lplGupfEwfDiFATgYqJJY4F7uRPEOuaH1KCWMcf7Y07/AFvT7ckAMtCdBSXTIri0DJE0i7X48Mi+QI6H7aNf2xW03x6X0Zx3CADPrmgenahHqunJJKR3iHpjnilLrQ9tJ7BV/pVxdXcksu0QRk9ABnzpls4/761bsrZQ+Lu403EcYBO859OGWhGpXUmokWVhGXMsmxVQcsSeg9qYv7JNPlftQEnXEsDNJLnnbt8IA/ryFUYruyLyGmqBPbq0x/a3PCh4jgDMR/L/AAj+pH30Au7ck5I4zR/VbpL/ALf9o9VAzG1wLWM+u0AH/wBY++oFZtevYi8SwgfOqDAAVVX8cVXiS4kHkSccl/CQFOimQBh8h5yKqGwiSUjxYXrkV0cacEjdViGxDjIOfIfuaX5UV5HLRjbnA96J412hWPyp21JEej2aT2l/EiKWmsZ0UkY8Xdkj8RSpa6f39pfXB47gAgY65PNdASIWVilzjYCDkgZwOg496XtK0x/72v8AST45GRlTaOHxyCPqMEUnJDaK8OVuMmHewfZO11HTfiLlC+CRtJ4zVvtdoGnW9vDtQB4VKrheQp6jOemaz2O1WTTtPWFCA4cghvL60bu7223fF3wWUr8q44BqFyaZ1IxTSYvdkeycl5J8ZehI4idyKRgv748hTtHo2lsil7SNmxycdaD6FrCXVzIdpLt1xwFHlTHBI4iUCMkeuKW5Wxyho5X290/XLm2jvbq5YwNIyrARgjB4OPPNCNKNrYabKizlppOqkdP9Kn1xbWfdK+oXs05OO7I4UenTiotKtmvxHY29rumeQFWJJam1SoTkVbGfsDALGHUO0Ey/wrCJhAWHDSngfd+tHewk40fstrnaSYePYUhz5nGFH5Utdq9Zt9Ns7XstpTq0cHiupQeJJD1yfTOfwozqdxazaJovZu0mjmt1AuL6SFtys3XYCOuOn3Vf42LmqObmnU0wTBows9H0+SRgZrkPcz88hmJwD77QtY7KXNpY6bqcl6shZrjuoxGuScq3v04NMetfDXMoghDbhG+cxkEHb7eVLVhGkFhcSuVbNyhxkdcN+/8ArVqwqUQJrdy3ZB2U0l9N1lbia3bbFE+/CYONvH0zgUzwaXaakYktWY8jr9OePrmoZdctLma8CToWeNNhClA2OvBPp60M0LURa6xA6Nj5IiPdiw/UUuUFFaIsjc8u+kOPafR0s+zUscScDYB/mzSS4n0S4sNe7h2FsUBG04kUeXvlcj7Kc9Xv5ruwmSfaIwD3e1s5A4yfvqtrd7ZT9m/gLhWRiqhW8OwbfMHPrWrF7N9jo51GXt6FrtLZpY66WsSWtblVubZ16OjDIP5j7Kp3InufAmXkI8Kigl3rzHRLTTJhmTT5W+Hm8zC3WM/Rskex9qzF2ikW0Mduds8nhDeYrk5YUzrYm6obbCwXTNJ7+TUPg5w4eRlIJP8A44qwe3ptT3MDwSRr8r7iM+fTaaTJdGu5Yd13qEGcZ25ags1qySsonUgHqDS1FFFyDd/2kS8Uqi4dicvio/8AiBbG1KaeAk8gw7qcvj0B/lH05+lBBZ8/LUotADuYYHoKdHEkQzzJlKVJZkkuGbGDk543ZPlTJpV+Z4y0Ld3eKxfKjh+nAHtzwPzqjaWi3d0i3BxCgPhzjijnaLSbezmtr+xeGLv/APmWsT8wMMY6eowfrVOPlDaEPPC+LDcmrWt1GkqyTQYXEo3+P/yGaWru+HcTJEW/5h2k4+UK2P0qKQMwE3ALcSKPP3qpOmQR/Xn+9W+r7NATyRl0FbqaNry3BIRAzJ4QBhQxx+FQNcubkzRjZteJhg8KR5/rVZN7TK5zwxPX3rwjbqOtJ5C33Ywz68UjAIDSgMo2nr05/Ogl/qOSzXL72BBWNeAOc81A6MBtXqep860Wzij8dwBI3lH+9Y8knpGwUY7fYIuXaYrhFVQDtwMZGSftx0qaxiAjW4zlQ2G55Q1Y+HZ5++fk7s8+tSiBEiAjiCyAbWIPDD0IqSUWyuOVIv7xdQ4efwgevNBZLYb22zcZ4zWHgkT5CQPSq/cy+ZNL9Nj1nT7GM258sCsC2znPmOvpWb2crdJGhIx196JRRB2C8c8DJqzijgSyyik38hnTZNPftBZ6fpWj2t3YMVt2aWEmadTjfKWzlWGCQRjAoJfxIt/cR2797DHK6ROP5lzwft6032FlZxafLZ6bqVtFcSqFu7tlfLKf+nHhThfU9SfaqEei7JCgIcAkBl6N7ihVWDmyuk+2U9C0u3FreanqEBuILXYiW+7aJpHzgMeu0AZOOvSrlm1vqtwllqui6bFbSnu1nsbbuZYCeAwIPiA8w2c0f0eyjjgns7pX+GuNpYoOUdTww9fMEelHNM0Wwt5UlMyzlCGVVjYZPlkmgnkjFD/GjmyVXRzVuzk9tczQSJl4ZGRiBwSDjIqez7NXF5P3UaqiqN0kkjbVRR1JNdWTRkld5JF3O5LMfc8msppUUMc8LgqsygFgOmDkVB/VLl1o7H8euzmfaTRNsME+npatp8AEKm2bcytjJMhKglm5OcY8hSy1kwb5T91devrGC3sbi2hbvHuCu7CkKoBz5+dLkmjqD8oq/FktbOZ5MJwl7Rd0a4v4e40+zsrKd3fbGJbOORiSfNiM4/KtO1z2/wAQljZxWxW2J7+4hiVO/mPzEY6IPlUe2fOmy2tRYWU08H/3pQYoyBzCh+Zv/wBEcD0pM1JfhrsQMo6enQ018eyZZckVT7ALQluMCovhwau3ri3BU8MRQsT8dTQuh0JuStGZ372UsvOAPspgSOWOB5dhIVSQfKle3aRd25GLY4bGaMRapdRwNavKohIOcKMkEdM0qOTbszLjbpfQd7ESSXt+9q/G5cg9AMc0731kbTT7iZWR2RM7c1zrsdqUFtrIHessjeEAoMHrx1prnvfiku2kDb96BwMgbeuB91BJt7PPipdbHG10qPYCQTvCk+I+XPrRKCx2HMW0E9d+4jrn1pTuO3dtFcR29lEXCjxsy8H8R99X9U7c2VrbjucmZ1G0Y8z+lRZJp6OlgnGI1rbuCjB4wwYsThsHnI8/rUcsDd4rFkyrFuN3OfbOKjtbiR7WJpcGQoC56c45rfvcuQeMVit6K3OPZVmsom/kPHTxnj8apLpsaOzIhyeOWJ/OjmzOM+dKPartLFErWWnFXZgd8oYgAe2MffmqI6IfIyxjFykE5oraBWM7hNo3HJ5x06Vzfth8N/ecs6SKYSEKtng+EGqevavOYozNcM83EaKTklc5I564zS49xJNGFjn7sbiQDjnn2609vicxyeeKaVKzXVbo3T5LqcZxtqgI2xxWCsibu8YKV6jFeV2IyFJHrit5FMI8VSN4iyAyBlKkkEP+9Ryzk7cY4PTOa1tO6mTDHYSccc81EVyACeh59cUoYorkXtGkkttWiljKg78AEeftXQZWyZnjI2zOrgjywP8AWuc28avGXbI2dSCAc+VO+mXpMQmmMaRGLvNxAGc+WPWtTpkvl2mpIs65qkWm2USWyg30o3RzRkZiw3LevOSPvoFo/wD8lq1v8W7OrzZlck5I+tD7y6+Nvnl+YbtqkDHHlTR2SsQWe5cnwuOT6D/ahcE2b6rhFfZ1mEMkZB8iRxVm0RmyzDk1St5pHQjCgfWrct0ttbvKxACjJxSeLTLo5I1YtdvdVtbOSO3cO9wsZYDdhAG45+wGkPTnOoai/eDMMMT3M5YY3qoOB7DoB9at6klxrGsG4vWJEjksBzhR0UfYMUd162tNH0W7kiJhe9iEawtgMgHLAeWcf0apjj+WcxTeeUpvo5vqLytPbq3zO0h2rjIPh/agk8jPkg4GTz+1FtSfa8EiRFVjUlVJ/wC4nqfUDFCriLu7fLYZgRz6f1zWN7K8SVI2fHwavOVLHBXAz99Ue9Pmw/y1NGxZdo5C5YisiYINuE+zFEkMiqMzRrEVEZ9/pUSsO8O/k5JrNwcMBnnFQ5/ibj5YFekthxVlrfstQU/6rZPPTH+9OUyxjRIbiORFZkCtv4zkcdB7NSMOAqDnBI++m69x/wAO2oVekUJI9G8Y/alytCPIjaSKMdqxKvGyOvqp6U59m7uC1sts7HGSVHd7sev6Up6I3cxyPLjb/wBpHzUyaH3WqOI5oYFRSCe7UA/dRR7pnOyuXOkG7jtlHaXtlZWo7zvZVEqmHohyMfMMEnpgHofWodR7VXN9FPbRqFj6Fjk4/oVz+VRcdpWigkGFuXSN0OeQW2H65A+6naXSozEheWKPdyV7wZzTFCLdj/JjkjBRTK8WoR2VuJX5AOFD52n1zihnabW5Nbukm2qohUrGgJKj39/KrWs2VqYlXf3z4wSj42n0xkUt3QggPdIrysxwse/oaGcifAnGPHZjWIzCtl3gIPAK+5VSfxzVLU0/xE3oGKjI646/j+dW+0UhkuYDv4LPxnPQ4/eq7nviJJGXYEG7LeJjS/06EXUUwdFtEc/uu39f0qrmrchjPGO7BHAFU8D1FNXRTBplliXiU45GRn1FbRWcsihguQTit425xxj6VcilkQnZ3fhPQEg0NiXOS6KkdtIxIEbcHBOOAaPWjLFptxb3UyBS0e1uoBB/ag8tzPuZoiFbGSq8jr15zg1PFqtzIzpvYIUxsIHiOMc4FE1fyBNSl8hXu1ZEKundn5WPn9nWjekJBaKZbwOqYyAyld/pgkdPOkVtQvO72xv3GCSGiOw598GsQXl1C3I3knkyEn8jmiTSBXjRrbGS91Gza7nlGmRW4Ur3abxsUiN8kHHuG6fy0bsL7Srq3SO8sbNJh1WI5J+o60ipL/ihKxiZTMHVJc4yOAM/b+FWJ7ibDdwERnOWAHA9wevNZy0MnGLDt/b2V2RHZRQwbOockP8AXB5/ChDW6WcyqikySHAZlwcfTy/OqIvL2FxKNneLxvGCfv64reTWZ3XEqBmzyMeKhcmxfpyXRjUWe5vduDtRmIJz0PJqpdzui9zG/wDCXP21aa5nkAMaSKQOR5c/0Kp92ZJMGMgnyIrF+jIKqv4K0UhBIJypqQIhGduKsNbbRwu49eo/eojE/wDKOKK0NtPaNe5JyBL064z1qZYnA5bGeCR6VTaTrsznrmvLK3COWx9aAJxYSaSOFVUFyxGNwGOfSopJQx8JHHPXNVHl5yvLZxnFehYI+Sgx6E9K9QCx0i33k5wVHgrU3MrZEkRI58ulaPeeLgE89aw00jHIYjI8QFePcX9EaF1fge/OeKkPflW2bgM56VtJKXOdq5zjNYaZvDhiADyBXjd/R7ZMudyPnz5ry97Gd2GzWrzuRkkjHUZ61hblkYggYHpXjakSxJO4YodgHJZjUjd5tyZ1z0G0dah71ivUEHjpxUHe5wIyQAcYrxnFs3ZpEYFyXxkg17vh5hj71YRoggYnOepI/Ssd/EecR/acV49f4f/Z",
        ]
    }
    # Create movie
    response = client.post("/v1/movies", json=user_dict, headers=auth_header)
    assert response.status_code == HTTP_201_CREATED
    assert 'id' in response.json()
    global new_movie_id
    new_movie_id = response.json().get('id')
