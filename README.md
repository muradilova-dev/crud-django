# Django: blog (List/Detail + лайки), crud (CRUD), reports (тесты -> Word)

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py test                 # запуск всех тестов
    python manage.py export_tests_docx    # запустить тесты и записать их в tests_report.docx
    python manage.py runserver

Адреса: /blog/  /blog/<id>/  /crud/  /crud/create/  /crud/<id>/update/  /crud/<id>/delete/  /admin/

Отчёт только по одному приложению: python manage.py export_tests_docx crud -o crud_report.docx
