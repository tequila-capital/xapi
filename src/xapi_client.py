import os
from enum import Enum

import grpc

import grpc_generated.order_pb2 as ord
import grpc_generated.order_pb2_grpc as ord_grpc
import grpc_generated.utilities_pb2 as util
import grpc_generated.utilities_pb2_grpc as util_grpc


class OrderSide(Enum):
    NONE = -1
    BUY = 0
    SELL = 1

    def __str__(self):
        return super().__str__().removeprefix('OrderSide.')


class XapiClient:
    __server: str
    __user: str
    __domain: str
    __password: str
    __locale: str
    __account: str
    __route: str
    __port: int
    # __pem_path: str
    __cert: bytes
    __channel: grpc.Channel
    __connect_response: util.ConnectResponse

    def __init__(
        self,
        server: str,
        user: str,
        domain: str,
        password: str,
        locale: str,
        account: str,
        route: str,
        port: int,
        pem_path: str,
    ):
        self.__server = server
        self.__user = user
        self.__domain = domain
        self.__password = password
        self.__locale = locale
        self.__account = account
        self.__route = route
        self.__port = port
        self.__channel = None
        # self.__pem_path = pem_path

        if not os.path.exists(pem_path):
            raise FileNotFoundError(f'Certificate not found at path {pem_path}')

        with open(pem_path, 'rb') as f:
            self.__cert = f.read()

    def __enter__(self):
        self.connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        self.disconnect()

        if self.__channel:
            self.__channel.close()
            self.__channel = None

    def __del__(self) -> None:
        self.close()

    def connect(self) -> None:
        self.__channel = grpc.secure_channel(
            f'{self.__server}:{self.__port}',
            grpc.ssl_channel_credentials(root_certificates=self.__cert),
        )

        util_stub = util_grpc.UtilityServicesStub(self.__channel)
        connect_request = util.ConnectRequest(
            UserName=self.__user,
            Domain=self.__domain,
            Password=self.__password,
            Locale=self.__locale,
        )

        self.__connect_response = util_stub.Connect(connect_request)
        print('Connect result: ', self.__connect_response.Response)

    def disconnect(self) -> None:
        if self.is_connected():
            util_stub = util_grpc.UtilityServicesStub(self.__channel)
            disconect_request = util.DisconnectRequest(UserToken=self.__connect_response.UserToken)

            disconnect_response = util_stub.Disconnect(disconect_request)
            print('Disconnect result: ', disconnect_response.ServerResponse)

            self.__connect_response = None

    def is_connected(self) -> bool:
        return (
            self.__connect_response is not None and self.__connect_response.Response == 'success'
        )

    def __get_token(self) -> str:
        return self.__connect_response.UserToken

    def submit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        order_tag: str,
    ) -> ord.SubmitSingleOrderResponse:
        if self.is_connected():
            try:
                ord_stub = ord_grpc.SubmitOrderServiceStub(self.__channel)
                order_request = ord.SubmitSingleOrderRequest(
                    Symbol=symbol,
                    Side=side,
                    Quantity=quantity,
                    Route=self.__route,
                    Account=self.__account,
                    OrderTag=order_tag,
                    UserToken=self.__get_token(),
                )

                order_response = ord_stub.SubmitSingleOrder(order_request)

                return order_response
            except Exception as e:
                print(f'{e}')

        raise (RuntimeError('Client not connected'))

    def cancel_order(self, order_tag: str) -> ord.ChangeSingleOrderResponse:
        if self.is_connected():
            try:
                ord_stub = ord_grpc.SubmitOrderServiceStub(self.__channel)

                cancel_request = ord.CancelSingleOrderRequest(
                    OrderId=order_tag,
                    UserToken=self.__get_token(),
                )

                cancel_response = ord_stub.CancelSingleOrder(cancel_request)

                return cancel_response
            except Exception as e:
                print(f'{e}')

        raise (RuntimeError('Client not connected'))

    def get_order_detail_by_order_id(self, order_id: str) -> list[ord.OrderDetailsResponse]:
        if self.is_connected():
            try:
                ord_stub = ord_grpc.SubmitOrderServiceStub(self.__channel)

                detail_request = ord.OrderDetailByOrderIdRequest(
                    OrderId=order_id,
                    UserToken=self.__get_token(),
                )

                detail_response = ord_stub.GetOrderDetailByOrderId(detail_request)

                return detail_response
            except Exception as e:
                print(f'{e}')

        raise (RuntimeError('Client not connected'))

    # TODO; Finish implementation
    # def get_order_detail_by_date_range(self, param):
    #     if self.is_connected():
    #         try:
    #             ord_stub = ord_grpc.SubmitOrderServiceStub(self.__channel)

    #             detail_request = ord.OrderDetailByDateRangeRequest(
    #                 UserToken=self.__get_token(),
    #             )

    #             detail_response = ord_stub.GetOrderDetailByDateRange(detail_request)

    #             return detail_response
    #         except Exception as e:
    #             print(f'{e}')

    #     raise (RuntimeError('Client not connected'))

    def get_order_detail_by_order_tag(
        self,
        order_tags: list[str],
        event_type: str,
    ) -> list[ord.OrderDetailsResponse]:
        if self.is_connected():
            try:
                ord_stub = ord_grpc.SubmitOrderServiceStub(self.__channel)

                detail_request = ord.OrderDetailByOrderTagRequest(
                    OrderTags=order_tags,
                    OrderEventType=event_type,
                    UserToken=self.__get_token(),
                )

                detail_response = ord_stub.GetOrderDetailByOrderTag(detail_request)

                return detail_response
            except Exception as e:
                print(f'{e}')

        raise (RuntimeError('Client not connected'))
