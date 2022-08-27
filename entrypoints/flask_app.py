from flask import Flask, request


import domain.model as model
import adapters.repository as repository
import services_layer.services as services

app = Flask(__name__)


@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    repo = repository.SqlAlchemyRepository()
    line = model.OrderLine(
        request.json["orderid"], request.json["sku"], request.json["qty"],
    )
    try:
        batchref = services.allocate(line, repo)
    except (model.OutOfStock, services.InvalidSku) as e:
        return {"message": str(e)}, 400

    return {"batchref": batchref}, 201