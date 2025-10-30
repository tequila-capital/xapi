import grpc
import order_pb2 as ord
import order_pb2_grpc as ord_grpc
import utilities_pb2 as util
import utilities_pb2_grpc as util_grpc
from example_base import ExampleBase


class PlaceOrderExample(ExampleBase):
    def __init__(self):
        super().__init__()
        self.my_order_id = 'MyOrderId'

    def run(self):
        with open(self.pem_path, 'rb') as f:
            cert = f.read()
        channel = grpc.secure_channel(
            f'{self.server}:{self.port}',
            grpc.ssl_channel_credentials(root_certificates=cert),
        )
        util_stub = util_grpc.UtilityServicesStub(channel)

        connect_response = util_stub.Connect(
            util.ConnectRequest(
                UserName=self.user,
                Domain=self.domain,
                Password=self.password,
                Locale=self.locale,
            )
        )
        print('Connect result: ', connect_response.Response)

        if connect_response.Response == 'success':
            ord_stub = ord_grpc.SubmitOrderServiceStub(channel)
            order_response = ord_stub.SubmitSingleOrder(
                ord.SubmitSingleOrderRequest(
                    Symbol='VOD.LSE',
                    Side='BUY',
                    Quantity=10,
                    Route=self.route,
                    Account=self.account,
                    OrderTag=self.my_order_id,
                    UserToken=connect_response.UserToken,
                )
            )
            print('Order result: ', order_response)

            disconnect_response = util_stub.Disconnect(
                util.DisconnectRequest(UserToken=connect_response.UserToken)
            )
            print('Disconnect result: ', disconnect_response.ServerResponse)


if __name__ == '__main__':
    example = PlaceOrderExample()
    example.run()
