import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import keyboard as k
from fake_useragent import UserAgent
import requests

ua = UserAgent()
bot = Bot(token='put your telegram bot token here', parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

connection = sqlite3.connect('data.db')
q = connection.cursor()


#############
# menu
@dp.message_handler(text=['/start', 'menu', 'Menu'])  # Начало работы
async def start(message: types.Message):
    q.execute(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    result = q.fetchall()
    if len(result) == 0:
        await message.answer('''
        Привет, я бот, созданный для отслеживания рынка Let Me Speak.
        У тебя пока нет доступа ко мне. Запросить доступ можно здесь: https://t.me/zeuspray
        Оплата возможна в любых токенах, в том числе LSTAR.
        Канал бота: @LetMeSpeakTracker_bot
        
        Hi, I'm a bot built to track the Let Me Speak market.
        You don't have access to me yet. Request access here: https://t.me/zeuspray
        Payment is possible in any tokens, including LSTAR
        Bot's сhannel: @LetMeSpeakTracker_bot''', parse_mode='Markdown')
    else:
        await message.answer(f'''Hi, {message.from_user.mention}!''', reply_markup=k.menu)


@dp.message_handler(text='LSTAR price')
async def lstar_price(message: types.Message):
    url = 'https://public-api.birdeye.so/public/price?address=C6qep3y7tCZUJYDXHiwuK46Gt6FsoxLi8qV1bTCRYaY1'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    items = data.get('data')
    value = items.get('value')
    try:
        await message.answer(f'''
Price of the LSTAR token right now: {round(value, 5)}$

10 LSTAR = {round(value * 10, 2)}$
100 LSTAR = {round(value * 100, 2)}$
500 LSTAR = {round(value * 500, 2)} $

Your can trade your LSTAR here:
https://birdeye.so/token/C6qep3y7tCZUJYDXHiwuK46Gt6FsoxLi8qV1bTCRYaY1
''')
    except:
        await message.answer('Something went wrong! Try later.')


class FSMAdd(StatesGroup):
    rank = State()
    freq = State()
    last = State()
    add = State()
    delete = State()


class FSMnft(StatesGroup):
    analyze = State()


#############
# price track
@dp.message_handler(text='Price tracking')
async def price_tracking(message: types.Message):
    q.execute(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    result = q.fetchall()
    task_ = []
    for task in result:
        for i in task:
            task_.append(i)

    if task_[3] == 1:
        await message.answer(f'''Already checking''', reply_markup=k.track)
        await checking_start(message)

    else:
        await cm_start(message)


#############
# stop price track
@dp.message_handler(text='Stop Tracking')
async def stop_traking(message: types.Message):
    q.execute(
        f"UPDATE users SET checking = 0 WHERE user_id = {message.chat.id}")
    connection.commit()
    await start(message)


#############
# edit tracking options
@dp.message_handler(text='Edit Tracking', state=None)
async def cm_start(message: types.Message, state=FSMContext):
    # rand_numb = random.randint(10000, 99999)
    # now = datetime.datetime.now()
    # q.execute(f"INSERT INTO tasks (task_id, user_id, task_desc, inv_amount, time)"
    #           f"VALUES ('{rand_numb}', '{message.chat.id}', 'Пока задания нет', '0', '{now}')")
    # connection.commit()
    await FSMAdd.rank.set()
    await message.reply("What rank to track?", reply_markup=k.rank)


@dp.message_handler(state=FSMAdd.rank)
async def get_rank(message: types.Message, state=FSMContext):
    q.execute(
        f"UPDATE users SET rank = '{message.text}' WHERE user_id = '{message.chat.id}'")
    connection.commit()

    await FSMAdd.next()
    await message.reply(f"How often to notify you?", reply_markup=k.freq)


@dp.message_handler(state=FSMAdd.freq)
async def get_freq(message: types.Message, state=FSMContext):
    msg = message.text
    if msg == 'Every 1 min':
        q.execute(
            f"UPDATE users SET freq = 1 WHERE user_id = {message.chat.id}")
        connection.commit()
    elif msg == 'Every 5 min':
        q.execute(
            f"UPDATE users SET freq = 5 WHERE user_id = {message.chat.id}")
        connection.commit()
    elif msg == 'Every 10 min':
        q.execute(
            f"UPDATE users SET freq = 10 WHERE user_id = {message.chat.id}")
        connection.commit()

    await FSMAdd.next()

    q.execute(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
    result = q.fetchall()
    task_ = []
    for task in result:
        for i in task:
            task_.append(i)
    await message.reply(f"""
Check your answers⚡️
Rank: {task_[1]}
Frequency: {task_[2]} min""", reply_markup=k.task_apr)


@dp.message_handler(state=FSMAdd.last)
async def get_last(message: types.Message, state=FSMContext):
    msg = message.text
    if msg == 'All right':

        await message.reply(f"""Started! I will send you a notification once there is a low price NFT""")
        q.execute(
            f"UPDATE users SET checking = 1 WHERE user_id = {message.chat.id}")
        connection.commit()
        await state.finish()
        await start(message)
        await checking_start(message)

    elif msg == 'Again':
        q.execute(
            f"UPDATE users SET rank = 0 WHERE user_id = {message.chat.id}")
        connection.commit()
        q.execute(
            f"UPDATE users SET freq = 0 WHERE user_id = {message.chat.id}")
        connection.commit()
        await state.finish()
        await cm_start(message)

    else:
        q.execute(
            f"UPDATE users SET rank = 0 WHERE user_id = {message.chat.id}")
        connection.commit()
        q.execute(
            f"UPDATE users SET freq = 0 WHERE user_id = {message.chat.id}")
        connection.commit()
        await state.finish()
        await start(message)


#############
# add user
@dp.message_handler(text='Добавить_zeus', state=None)
async def add(message: types.Message):
    await FSMAdd.add.set()
    await message.reply("link")


@dp.message_handler(state=FSMAdd.add)
async def add_start(message: types.Message, state=FSMContext):
    q.execute(f"INSERT INTO users (user_id)"
              f"VALUES ('{message.text}')")
    connection.commit()
    await message.answer('Добавил', reply_markup=k.menu)
    await state.finish()


class FMSfloor(StatesGroup):
    question = State()
    uncommon = State()
    rare = State()
    epic = State()
    legendary = State()
    ask = State()


#############
# delete user


@dp.message_handler(text='Удалить_zeus', state=None)
async def delete(message: types.Message):
    await FSMAdd.delete.set()
    await message.reply("link")


@dp.message_handler(state=FSMAdd.delete)
async def delete_start(message: types.Message, state=FSMContext):
    q.execute(f"DELETE FROM users WHERE user_id={message.text}")
    connection.commit()
    await message.answer('Удалил', reply_markup=k.menu)
    await state.finish()


async def checking_start(message: types.Message):
    while True:
        q.execute(f"SELECT * FROM users WHERE user_id = {message.chat.id}")
        result = q.fetchall()
        task_ = []

        for task in result:
            for i in task:
                task_.append(i)
        if task_[3] == 1 and task_[1] == 'Uncommon':
            try:
                result_ = await collect_data_uncommon()
                average_floor_of_rarity = await floor(2)
                if result_ == []:
                    await asyncio.sleep(int(task_[2]) * 60)
                else:
                    await message.answer(f"""
Quick flip this NFT!
Rarity: Uncommon
Visa: {result_[0]['visa_left']}/120
Talent: {result_[0]['talent']}
Invites left: {result_[0]['invites_left']}

Price: {result_[0]['price']}$
Average floor: {average_floor_of_rarity}
Your profit from resale: {round(average_floor_of_rarity - result_[0]['price'],2)}$
Link: {result_[0]['item_id']}""")
                    await asyncio.sleep(int(task_[2]) * 60)

            except:
                pass

        elif task_[3] == 1 and task_[1] == 'Rare':
            try:
                result_ = await collect_data_rare()
                average_floor_of_rarity = await floor(3)
                if result_ == []:

                    await asyncio.sleep(int(task_[2]) * 60)
                else:
                    await message.answer(f"""
Quick flip this NFT!
Rarity: Rare
Visa: {result_[0]['visa_left']}/150
Talent: {result_[0]['talent']}
Invites left: {result_[0]['invites_left']}

Price: {result_[0]['price']}$
Average floor: {average_floor_of_rarity}
Your profit from resale: {round(average_floor_of_rarity - result_[0]['price'],2)}$
Link: {result_[0]['item_id']}""")
                    await asyncio.sleep(int(task_[2]) * 60)

            except:
                pass

        elif task_[3] == 1 and task_[1] == 'Epic':
            try:
                result_ = await collect_data_epic()
                average_floor_of_rarity = await floor(4)
                if result_ == []:

                    await asyncio.sleep(int(task_[2]) * 60)
                else:
                    await message.answer(f"""
Quick flip this NFT!
Rarity: Epic
Visa: {result_[0]['visa_left']}/180
Talent: {result_[0]['talent']}
Invites left: {result_[0]['invites_left']}

Price: {result_[0]['price']}$
Average floor: {average_floor_of_rarity}
Your profit from resale: {round(average_floor_of_rarity - result_[0]['price'],2)}$
Link: {result_[0]['item_id']}""")
                    await asyncio.sleep(int(task_[2]) * 60)

            except:
                pass

        elif task_[3] == 1 and task_[1] == 'Legendary':
            try:
                result_ = await collect_data_legendary()
                average_floor_of_rarity = await floor(5)
                if result_ == []:

                    await asyncio.sleep(int(task_[2]) * 60)
                else:
                    await message.answer(f"""
Quick flip this NFT!
Rarity: Legendary
Visa: {result_[0]['visa_left']}/240
Talent: {result_[0]['talent']}
Invites left: {result_[0]['invites_left']}

Price: {result_[0]['price']}$
Average floor: {average_floor_of_rarity}
Your profit from resale: {round(average_floor_of_rarity - result_[0]['price'],2)}$
Link: {result_[0]['item_id']}""")
                    await asyncio.sleep(int(task_[2]) * 60)
            except:
                pass

        elif task_[3] == 1 and task_[1] == 'Every rank':
            try:
                result_ = await collect_data_every_rank()

                if result_ == []:

                    await asyncio.sleep(int(task_[2]) * 60)
                else:
                    for x in range(4):
                        if result_[x]:

                            await message.answer(result_[x][0])
                        else:
                            pass
                    await asyncio.sleep(int(task_[2]) * 60)

            except:
                pass
        else:
            break


async def collect_data_uncommon():
    result = []
    url = 'https://api-crypto.letmespeak.org/api/escrow?talentMin=20&talentMax=59&invitesDoneMin=0&invitesDoneMax=3&rarity=2&page=1&sortBy=LowestPrice'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    items = data.get('items')

    lowest_site = items[0]['price']
    average_floor_of_rarity = await floor(2)

    if (100 - (lowest_site * 100) / average_floor_of_rarity) > 10:
        item_id = items[0].get('id')
        price = items[0].get('price')
        talent = items[0].get('nft')
        if talent['details']['attributes'][12]['value'] >= 3:
            result.append(
                {
                    'item_id': 'https://market.letmespeak.org/#/escrow/' + item_id,
                    'price': price,
                    'talent': talent['details']['attributes'][2]['value'],
                    'invites_left': talent['details']['attributes'][12]['value'],
                    'rare': 'Uncommon',
                    "visa_left": talent['details']['attributes'][8]['value']
                }
            )

    return result


async def collect_data_rare():
    result = []

    url = 'https://api-crypto.letmespeak.org/api/escrow?talentMin=20&talentMax=59&invitesDoneMin=0&invitesDoneMax=3&rarity=3&page=1&sortBy=LowestPrice'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    items = data.get('items')

    lowest_site = items[0]['price']
    average_floor_of_rarity = await floor(3)

    if (100 - (lowest_site * 100) / average_floor_of_rarity) > 10:
        item_id = items[0].get('id')
        price = items[0].get('price')
        talent = items[0].get('nft')
        if talent['details']['attributes'][12]['value'] >= 3:
            result.append(
                {
                    'item_id': 'https://market.letmespeak.org/#/escrow/' + item_id,
                    'price': price,
                    'talent': talent['details']['attributes'][2]['value'],
                    'invites_left': talent['details']['attributes'][12]['value'],
                    'rare': 'Rare',
                    "visa_left": talent['details']['attributes'][8]['value']
                }
            )
    return result


async def collect_data_epic():
    result = []

    url = 'https://api-crypto.letmespeak.org/api/escrow?talentMin=20&talentMax=59&invitesDoneMin=0&invitesDoneMax=3&rarity=4&page=1&sortBy=LowestPrice'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    items = data.get('items')

    lowest_site = items[0]['price']
    average_floor_of_rarity = await floor(4)

    if (100 - (lowest_site * 100) / average_floor_of_rarity) > 10:
        item_id = items[0].get('id')
        price = items[0].get('price')
        talent = items[0].get('nft')
        if talent['details']['attributes'][12]['value'] >= 3:
            result.append(
                {
                    'item_id': 'https://market.letmespeak.org/#/escrow/' + item_id,
                    'price': price,
                    'talent': talent['details']['attributes'][2]['value'],
                    'invites_left': talent['details']['attributes'][12]['value'],
                    'rare': 'Epic',
                    "visa_left": talent['details']['attributes'][8]['value']
                }
            )

    return result


async def collect_data_legendary():
    result = []

    url = 'https://api-crypto.letmespeak.org/api/escrow?talentMin=20&talentMax=59&invitesDoneMin=0&invitesDoneMax=3&rarity=5&page=1&sortBy=LowestPrice'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    items = data.get('items')

    lowest_site = items[0]['price']
    average_floor_of_rarity = await floor(5)

    if (100 - (lowest_site * 100) / average_floor_of_rarity) > 10:
        item_id = items[0].get('id')
        price = items[0].get('price')
        talent = items[0].get('nft')
        if talent['details']['attributes'][12]['value'] >= 3:
            result.append(
                {
                    'item_id': 'https://market.letmespeak.org/#/escrow/' + item_id,
                    'price': price,
                    'talent': talent['details']['attributes'][2]['value'],
                    'invites_left': talent['details']['attributes'][12]['value'],
                    'rare': 'Legendary',
                    "visa_left": talent['details']['attributes'][8]['value']
                }
            )
    return result


async def collect_data_every_rank():
    result = []
    res_uncommon = []
    res_rare = []
    res_epic = []
    res_legendary = []

    uncommon = await collect_data_uncommon()
    rare = await collect_data_rare()
    epic = await collect_data_epic()
    legendary = await collect_data_legendary()

    floor_uncommon = await floor(2)
    floor_rare = await floor(3)
    floor_epic = await floor(4)
    floor_legendary = await floor(5)

    await asyncio.sleep(5)

    if uncommon:
        res_uncommon.append(f"""
Quick flip this NFT!
Rarity: Uncommon
Visa: {uncommon[0]['visa_left']}/120
Talent: {uncommon[0]['talent']}
Invites left: {uncommon[0]['invites_left']}

Price: {uncommon[0]['price']}$ 
Average floor: {floor_uncommon}$
Your profit from resale: {round(floor_uncommon - uncommon[0]['price'],2)}$
Link: {uncommon[0]['item_id']}
    """)

    if rare:
        res_rare.append(f"""
Quick flip this NFT!
Rarity: Rare
Visa: {rare[0]['visa_left']}/150
Talent: {rare[0]['talent']}
Invites left: {rare[0]['invites_left']}

Price: {rare[0]['price']}$
Average floor: {floor_rare}$
Your profit from resale: {round(floor_rare - rare[0]['price'],2)}$
Link: {rare[0]['item_id']}
        """)
    if epic:
        res_epic.append(f"""
Quick flip this NFT!
Rarity: Epic
Visa: {epic[0]['visa_left']}/180        
Talent: {epic[0]['talent']}
Invites left: {epic[0]['invites_left']}

Price: {epic[0]['price']}$
Average floor: {floor_epic}$
Your profit from resale: {round(floor_epic - epic[0]['price'],2)}$
Link: {epic[0]['item_id']}
        """)

    if legendary:
        res_legendary.append(f"""
Quick flip this NFT!
Rarity: Legendary
Visa: {legendary[0]['visa_left']}/240             
Talent: {legendary[0]['talent']}
Invites left: {legendary[0]['invites_left']}

Price: {legendary[0]['price']}$
Average floor: {floor_legendary}$
Your profit from resale: {round(floor_legendary - legendary[0]['price'],2)}$
Link: {legendary[0]['item_id']}
        """)

    result.append(res_uncommon)
    result.append(res_rare)
    result.append(res_epic)
    result.append(res_legendary)

    return result


@dp.message_handler(text=['Analyze my NFT'], state=None)
async def ask_nfts(message: types.Message):
    await FSMnft.analyze.set()
    await message.reply("""
Send me your NFT link. 
Example: https://market.letmespeak.org/#/inventory/8S..
or https://market.letmespeak.org/#/escrow/2B..""")


@dp.message_handler(state=FSMnft.analyze)
async def get_nfts(message: types.Message, state=FSMContext):
    nft_number = message.text.split(sep="/")
    try:
        if nft_number[4] == 'escrow':
            try:
                your_analysys = await analyze_nft_escrow(nft_number[5])
                await message.answer(your_analysys, parse_mode='markdown')
                await state.finish()
            except Exception as ex:
                await message.answer('Something went wrong. Try again or change the link.')
                await state.finish()

        elif nft_number[4] == 'inventory':
            try:
                your_analysys = await analyze_nft_inventory(nft_number[5])
                await message.answer(your_analysys)
                await state.finish()
            except:
                await message.answer('Something went wrong. Try again or change the link.')
                await state.finish()

        else:
            await message.answer('Something went wrong. Try again or change the link!')
            await state.finish()
    except:
        await message.answer('Something went wrong. Try again or change the link.')

        await state.finish()


async def analyze_nft_escrow(nft_number):
    # my nft
    talent_analys = []
    invites_analys = []

    url = f'https://api-crypto.letmespeak.org/api/escrow/{nft_number}'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    name = data.get('nft').get('details')

    items = data.get('nft').get('details').get('attributes')
    rarity = items[4]['value']
    average_floor_of_rarity = await floor(rarity)
    invites_left = items[12]['value']
    invites_done = items[18]['value']
    talent = items[2]['value']

    url2 = f'https://api-crypto.letmespeak.org/api/escrow?talentMin={talent}&talentMax={talent}&invitesDoneMin={invites_done}&invitesDoneMax={invites_done}&page=1&sortBy=LowestPrice'
    response2 = requests.get(
        url=url2,
        headers={'user-agent': f'{ua.random}'}
    )
    talent_data = response2.json()
    talent_price = talent_data.get('items')[0]['price']
    suggested_price = talent_price + (talent_price * 0.05)

    percent = round(100 - (round(((talent_price * 100) / suggested_price) - 100, 2)), 2)

    if rarity:
        if invites_left >= 4:
            invites_analys.append("High chance of selling")
            suggested_price = talent_price + (talent_price * 0.15)
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")

        elif invites_left >= 3:
            invites_analys.append("High chance of selling")
            suggested_price = talent_price + (talent_price * 0.10)
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")

        elif invites_left == 2:
            invites_analys.append("Medium chance of selling")
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")
        else:
            invites_analys.append("Low chance of selling")
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")
    else:
        pass

    final_result = f"""
👤Name: {name['name']}

👥Invites left: {invites_left} - {invites_analys[0]}

⭐️Talent: {talent} - {talent_analys[0]}

⚓️Average floor price by talent of your NFT: {talent_price}$

💎Your price: {data['price']}$

🛒Sale probability: {percent}%
"""

    return final_result

    # all nft first page


async def analyze_nft_inventory(nft_number):
    # my nft
    talent_analys = []
    invites_analys = []
    url = f'https://api-crypto.letmespeak.org/api/nfts/{nft_number}?byMint=true'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    name = data.get('details')
    items = data.get('details').get('attributes')
    invites_left = items[12]['value']
    invites_done = items[18]['value']
    talent = items[2]['value']
    rarity = items[4]['value']

    url2 = f'https://api-crypto.letmespeak.org/api/escrow?talentMin={talent}&talentMax={talent}&invitesDoneMin={invites_done}&invitesDoneMax={invites_done}&page=1&sortBy=LowestPrice'
    response2 = requests.get(
        url=url2,
        headers={'user-agent': f'{ua.random}'}
    )
    talent_data = response2.json()
    talent_price = talent_data.get('items')[0]['price']
    suggested_price = talent_price + (talent_price * 0.1)

    if rarity:
        if invites_left >= 4:
            invites_analys.append("High chance of selling")
            suggested_price = talent_price + (talent_price * 0.20)
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")

        elif invites_left >= 3:
            invites_analys.append("High chance of selling")
            suggested_price = talent_price + (talent_price * 0.15)
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")

        elif invites_left == 2:
            invites_analys.append("Medium chance of selling")
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")
        else:
            invites_analys.append("Low chance of selling")
            talent_analys.append(f"Suggested price ≈ {suggested_price}$")
    else:
        pass

    # floor_of_rarity = await floor(rarity)

    final_result = f"""
👤Name: {name['name']}

⚓️Floor price by talent of your NFT: {talent_price}$

⭐️Talent: {talent} - {talent_analys[0]}

👥Invites left: {invites_left} - {invites_analys[0]}
"""
    return final_result


async def floor(rarity):
    url = f'https://api-crypto.letmespeak.org/api/escrow?sortBy=LowestPrice&rarity={rarity}&page=1'
    response = requests.get(
        url=url,
        headers={'user-agent': f'{ua.random}'}
    )
    data = response.json()
    items = data.get('items')
    floor0 = items[0]['price']
    floor1 = items[1]['price']
    floor2 = items[2]['price']
    floor = round((floor0 + floor1 + floor2) / 3, 2)
    return floor


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
