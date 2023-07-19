# Technical notes

## dev cheatsheet


```
docker-compose build
docker-compose up
docker exec -it zero bash
```

Run tests

```
docker exec -it zero  python -m pytest -s test_basics.py
docker exec -it zero  python -m pytest -s test_basics.py::TestTDD::test_streamlit_chain
```
