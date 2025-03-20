from .print_fonts import PrintFonts


class TelegramBot():
    def help(self):
        """Get all methods with descriptions"""
        pf = PrintFonts()
        text = f"""
        ## TELEGRAM BOT
        ! Here you can find how to quickly setup your own Telegram Bot with python-telegram-bot module

        # Imports:
        -imports() = Find the most common imports to start 

        # Methods:
        -quick_start() = Quick setup explanations
        """
        pf.format(text)

    def imports(self):
        """Write imports"""
        pf = PrintFonts()

        text = f"""
        ## MOST USED IMPORTS FOR TELEGRAM BOT

        from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup, Bot
        from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
        import asyncio
        """
        pf.format(text)

    def quick_start(self):
        """Quick setup and explanations"""
        pf = PrintFonts()

        text = """  
        ## QUICK START - Setup your own Telegram Bot

        ## Most Important Functions
        
        # After you have received the Telegram Bot Token from Telegram BOT FATHER 
        TOKEN = "write your token"

        # One of the most useful functions: this will be trigged whenever the user clicks on "/start"
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            ! Create this function, usually making the bot send intro messages, example below
            await update.message.reply_text('Welcome!')
        
        
        # Function that enables the bot to answer
        async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Get the message of the user
            received_text = update.message.text.lower()
            
            # Search if the user write a message to enable interactions
            if "message" in received_text:
                keyboard = [
                    [InlineKeyboardButton("Example A", callback_data='examplea')],
                    [InlineKeyboardButton("Example B", callback_data='exampleb')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text("Possible Examples:", reply_markup=reply_markup)
        
        
        # Function that enables interactions after the user clicks on a button
        async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Get the button clicked by the user
            query = update.callback_query
            await query.answer()
            button_clicked = query.data
        
            if button_clicked == 'examplea':
                await update.callback_query.message.reply_text("You have clicked on Example A!")
            elif button_clicked == 'exampleb':
                await update.callback_query.message.reply_text("You have clicked on Example B!")
        
        ! You can create your own functions with async def "your_function"(update: Update, context: ContextTypes.DEFAULT_TYPE):
        ! Then you have to add them in the Bot Comands List at the end of file
        
        
        
        ## Optional but important code to use in your functions
        # Save/Use info of the user
        user = update.effective_user
        
        # Let the bot write a message
        await update.message.reply_text('Message')
        # Let the bot write a message after waiting user message
        await update.callback_query.message.reply_text('Message')
        
        # Button list that triggers their messages in the button function 
        keyboard = [
            [InlineKeyboardButton("Example A", callback_data='examplea')],
            [InlineKeyboardButton("Example B", callback_data='exampleb')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("What do you want to read?", reply_markup=reply_markup)
        
        
        
        ## End of file, real Bot Configurations
        
        # Enable Bot
        application = Application.builder().token(TOKEN).build()
        
        # List every Bot Comands (functions)
        application.add_handler(CommandHandler('start', start))
        ! Add all your functions too
        application.add_handler(CommandHandler('your_function', your_function))
        
        # Functions to make the bot answer and enable its buttons
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
        application.add_handler(CallbackQueryHandler(buttons))
        
        # Start Bot
        application.run_polling()
        """
        pf.format(text)

