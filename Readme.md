**users_balance** Api for working with user balances. Created with DRF

# Quick start

##### Download image from docker hub

---
```
docker pull sergeynaum/users_balance:latest
```
---
##### Start the container by running the command
```
make docker_start
```
---
##### CONGRATULATIONS THE CONTAINER IS UP AND RUNNING AND THE API IS READY FOR TESTING_🚀

---
### Available methods for API requestsAvailable methods for API requests

Output wallets of all users by GET method
```
curl http://127.0.0.1:8000/api/v1/balance/
```

Getting wallet of a certain user by id GET method

```
curl http://127.0.0.1:8000/api/v1/balance/{id}/
```

Replenishment of user balance by PUT method id

```
curl -X PUT -H "Content-Type: application/json" -d '{"amount": 100}' http://127.0.0.1:8000/api/v1/balance/{id}/increase/
```

WITHDRAWAL of funds from user's balance by id PUT method

```
curl -X PUT -H "Content-Type: application/json" -d '{"amount": 100}' http://127.0.0.1:8000/api/v1/balance/{id}/decrease/
```

Getting user's balance by his id GET method currency parameter can contain 2 values RUB and USD
```
curl http://127.0.0.1:8000/api/v1/balance/{id}/get_user_blnc/?currency=RUB
```

Retrieving user transactions by user id

```
curl http://127.0.0.1:8000/api/v1/balance/{id}/list_user_transactions/
```

Transfer of funds from 1 user to another user

```
curl -X POST -H "Content-Type: application/json" -d '{"sender_id": "{id}", "receiver_id": "{id}", "amount": 100}' http://127.0.0.1:8000/api/v1/balance/p2p/
```
