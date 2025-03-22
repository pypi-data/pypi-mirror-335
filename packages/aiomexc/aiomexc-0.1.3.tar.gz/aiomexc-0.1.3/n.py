from datetime import datetime

from aiomexc.ws.proto.public_aggre_deals import (
    PublicAggreDealsMessage,
    PublicAggreDealItemMessage,
)

m = PublicAggreDealsMessage(
    deals=[
        PublicAggreDealItemMessage(
            price="0.077832", quantity="517.2", trade_type=2, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077831", quantity="308.12", trade_type=1, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077837", quantity="467.02", trade_type=1, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077829", quantity="349.94", trade_type=1, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.07783", quantity="550.65", trade_type=2, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077833", quantity="743", trade_type=2, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077828", quantity="57.23", trade_type=2, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077836", quantity="333.21", trade_type=1, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077834", quantity="826.63", trade_type=1, time=1742507863061
        ),
        PublicAggreDealItemMessage(
            price="0.077835", quantity="124.14", trade_type=2, time=1742507863061
        ),
    ],
    event_type="spot@public.aggre.deals.v3.api.pb@10ms",
)

sorted_by_time = sorted(m.deals, key=lambda x: x.time)

for deal in sorted_by_time:
    print(deal)
