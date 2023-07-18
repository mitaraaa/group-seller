instruction =
    <b>Before buying, please read the following information:</b>

    <pre>1. Make sure that your account does not have a limit, as in this photo.
    </pre>
    <i>*click <a href="https://help.steampowered.com/en/wizard/HelpWithLimitedAccount">here</a>, to check</i>

    <pre>2. You can only own 10 groups at a time.
    </pre>
    <i>*make sure you have a free slot</i>

    <pre>3. Payment by card is available only when choosing the Russian language. To change, write /language
    </pre>

    <pre>4. After payment, you will get full access to the account that owns the group. To get account information, send me your order number here:
    </pre>
    <tg-spoiler>@worker</tg-spoiler>

language_set = Picked language: :United_States: English
profile =
    Name: <code>{ $name }</code>
    User ID: <code>{ NUMBER($id, useGrouping: 0) }</code>
    Orders amount: <code>{ $orders_amount }</code>
    Orders total: <code>{ $orders_sum }</code>
choosing_group = Choose a group:
group_info = 
    "<a href="{ $link }">{ $name }</a>"

    Name: <code>{ $name }</code>
    Tag: <code>{ $tag }</code>
    URL: <code>{ $url }</code>

    <i>Founded</i>
    <i>{ $founded }</i>
continue = :check_mark_button: Continue
back = :BACK_arrow: Back
payment_option_btc = Bitcoin (BTC) - <code>{ $price }</code>
payment_option_eth = Ethereum (ETH) - <code>{ $price }</code>
payment_option_usdt = Tether (USDT) - <code>{ $price }</code>
payment_option_ton = Toncoin (TON) - <code>{ $price }</code>
payment_option_button_btc = Bitcoin (BTC)
payment_option_button_eth = Ethereum (ETH)
payment_option_button_usdt = Tether (USDT)
payment_option_button_ton = Toncoin (TON)
order = 
    ➖➖➖➖➖➖➖➖➖➖➖➖
    ⚜️ Group: <code>{ $name }</code>
    💵 Price: <code>{ $price }</code>
    📦 Order: <code>{ $order_id }</code>
    💲 Payment method: <code>{ $payment_option }</code>
    ➖➖➖➖➖➖➖➖➖➖➖➖
    For payment follow the link
    ⏰ Time remaining: <code>{ $time_remaining } minutes</code>
    🕜 Deadline: <code>{ $time_until }</code>
    ➖➖➖➖➖➖➖➖➖➖➖➖
proceed_button = Proceed to checkout