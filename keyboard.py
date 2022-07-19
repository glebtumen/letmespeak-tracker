from aiogram import Bot, Dispatcher, executor, types


menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
menu.add(
    types.KeyboardButton('Price tracking'),
    types.KeyboardButton('LSTAR price'),
    types.KeyboardButton('Analyze my NFT'),
)


rank = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
rank.add(
    types.KeyboardButton(text='Uncommon'),
    types.KeyboardButton(text='Rare'),
    types.KeyboardButton(text='Epic'),
    types.KeyboardButton(text='Legendary'),
    types.KeyboardButton(text='Every rank')
)


freq = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
freq.add(
    types.KeyboardButton(text='Every 1 min'),
    types.KeyboardButton(text='Every 5 min'),
    types.KeyboardButton(text='Every 10 min'),
)


track = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
track.add(
    types.KeyboardButton('Stop Tracking'),
    types.KeyboardButton('Edit Tracking'),
    types.KeyboardButton('Menu')
)

task_apr = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
task_apr.add(
    types.KeyboardButton(text='All right'),
    types.KeyboardButton(text='Again'),
    types.KeyboardButton(text='Menu')
)

admin = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
admin.add(
    types.KeyboardButton(text='add'),
    types.KeyboardButton(text='delete'),
    types.KeyboardButton(text='menu')
)

nfts = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
nfts.add(
    types.KeyboardButton(text='Add more'),
    types.KeyboardButton(text='Clear'),
    types.KeyboardButton(text='Menu')
)

refresh = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
refresh.add(
    types.KeyboardButton(text='Again'),
    types.KeyboardButton(text='Menu')
)