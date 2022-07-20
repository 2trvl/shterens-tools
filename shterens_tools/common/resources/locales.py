import inspect
from .mongodb import *

async def locale_string_by_id(string: str, id: types.base.Integer) -> str:
    return locales[string][await lang_by_id(id)]


locales = {
    "select-language": inspect.cleandoc("""
        [ EN ] Select language
        [ ES ] Seleccione el idioma
        [ FR ] Sélectionner la langue
        [ PT ] Seleccionar idioma
        [ RU ] Выберите язык
        [ ZH ] 选择语言"""),
    "commands": {
        "en": {
            "/getstats": "Get statistics for the channel",
            "/add": "Add bot to your channel",
            "/channels": "Manage your channels",
            "/language": "Change language",
            "/help": "Help",
            "/cancel": "Cancel tasks"
        },
        "es": {
            "/getstats": "Obtener estadísticas del canal",
            "/add": "Añade un bot a tu canal",
            "/channels": "Gestione sus canales",
            "/language": "Cambiar el idioma",
            "/help": "Ayuda",
            "/cancel": "Cancelar tareas"
        },
        "fr": {
            "/getstats": "Obtenir des statistiques pour le canal",
            "/add": "Ajoutez un robot à votre chaîne",
            "/channels": "Gérez vos canaux",
            "/language": "Changer de langue",
            "/help": "Aide",
            "/cancel": "Annuler les tâches"
        },
        "pt": {
            "/getstats": "Obter estatísticas para o canal",
            "/add": "Adicione bot ao seu canal",
            "/channels": "Gerir os seus canais",
            "/language": "Mudar idioma",
            "/help": "Ajuda",
            "/cancel": "Cancelar tarefas"
        },
        "ru": {
            "/getstats": "Получение статистики для канала",
            "/add": "Добавить бота в свой канал",
            "/channels": "Управление вашими каналами",
            "/language": "Изменить язык",
            "/help": "Справка",
            "/cancel": "Отменить все задачи"
        },
        "zh": {
            "/getstats": "获取通道的统计数据",
            "/add": "在你的频道中添加机器人",
            "/channels": "管理你的渠道",
            "/language": "改变语言",
            "/help": "帮助",
            "/cancel": "取消任务"
        }
    },
    "welcome":
    {
        "en": inspect.cleandoc("""
            👋 Welcome to Shteren's tools. To use the bot in chats, start your message with @shterensToolsBot

            <b>Service</b>
            /language – Change language
            /help – Send this message
            /cancel – Cancel tasks
        
            <b>Channels</b>
            /add – Add a bot to your channel
            /channels – Manage your channels
        
            <b>Statistics</b>
            /getstats – Get statistics for the channel
        
            💬 Questions & Suggestions: @shteren"""),
        
        "es": inspect.cleandoc("""
            👋 Bienvenido a las herramientas de Shteren. Para utilizar el bot en los chats, comienza tu mensaje con @shterensToolsBot
        
            <b>Servicio</b>
            /language – Cambiar el idioma
            /help – Enviar este mensaje
            /cancel – Cancelar tareas
        
            <b>Canales</b>
            /add – Añadir un bot a su canal
            /channels – Gestiona tus canales
        
            <b>Estadísticas</b>
            /getstats – Obtener estadísticas del canal
        
            💬 Preguntas y sugerencias: @shteren"""),

        "fr": inspect.cleandoc("""
            👋 Bienvenue sur le site des outils de Shteren. Pour utiliser le robot dans les chats, commencez votre message par @shterensToolsBot
        
            <b>Service</b>
            /language – Changer de langue
            /help – Envoyer ce message
            /cancel – Annuler les tâches
        
            <b>Canaux</b>
            /add – Ajouter un robot à votre canal
            /channels – Gérez vos canaux
        
            <b>Statistiques</b>
            /getstats – Obtenir des statistiques pour le canal
        
            💬 Questions et suggestions : @shteren"""),

        "pt": inspect.cleandoc("""
            👋 Bem-vindo às ferramentas da Shteren. Para usar o bot em chats, comece a sua mensagem com @shterensToolsBot
        
            <b>Serviço</b>
            /language – Mudar idioma
            /help – Enviar esta mensagem
            /cancel – Cancelar tarefas
        
            <b>Canais</b>
            /add – Adicione um bot ao seu canal
            /channels – Gerir os seus canais
        
            <b>Estatísticas</b>
            /getstats – Obter estatísticas para o canal
        
            💬 Perguntas & sugestões: @shteren"""),
        
        "ru": inspect.cleandoc("""
            👋 Добро пожаловать в инструменты Штерена. Для использования бота в чатах начните ваше сообщение с @shterensToolsBot
        
            <b>Сервис</b>
            /language – Поменять язык
            /help – Отправить это сообщение
            /cancel – Отменить задачи
        
            <b>Каналы</b>
            /add – Добавить бота в ваш канал
            /channels – Управление вашими каналами
        
            <b>Статистика</b>
            /getstats – Получить статистику для канала
        
            💬 Вопросы и предложения: @shteren"""),

        "zh": inspect.cleandoc("""
            👋 欢迎来到Shteren的工具。要在聊天中使用机器人，请以@shterensToolsBot开始您的信息。
        
            <b>服务</b>
            /language – 改变语言
            /help – 发送此消息
            /cancel – 取消任务
        
            <b>频道</b>
            /add – 在你的频道中添加一个机器人
            /channels – 管理你的频道
        
            <b>统计数据</b>
            /getstats – 获取频道的统计数据
        
            💬 问题和建议。@shteren""")
    },
    "cancel":
    {
        "en": "All tasks cancelled",
        "es": "Todas las tareas canceladas",
        "fr": "Toutes les tâches sont annulées",
        "pt": "Todas as tarefas canceladas",
        "ru": "Все задачи отменены",
        "zh": "所有任务被取消"
    },
    "getstats-steps":
    {
        "en": inspect.cleandoc("""
            📊 Okay, let's collect statistics of the channel. To do this, we'll go through the <b>following 4 steps:</b>
        
            1. Choose a channel
            2. Check access to it
            3. Define the range of messages
            4. Compile tagging preferences"""),

        "es": inspect.cleandoc("""
            📊 Bien, vamos a recoger las estadísticas del canal. Para ello, realizaremos los <b>siguientes 4 pasos:</b>
        
            1. Elegir un canal
            2. Comprobar el acceso al mismo
            3. Defina el rango de los mensajes
            4. Compilar las preferencias de etiquetado"""),

        "fr": inspect.cleandoc("""
            📊 Ok, collectons les statistiques de la chaîne. Pour ce faire, nous allons passer par <b>les 4 étapes suivantes:</b>
        
            1. Choisissez un canal
            2. Vérifier son accès
            3. Définir la portée des messages
            4. Compiler les préférences de balisage"""),

        "pt": inspect.cleandoc("""
            📊 Muito bem, vamos recolher estatísticas do canal. Para tal, vamos percorrer <b>os 4 passos seguintes:</b>

            1. Escolher um canal
            2. Verificar o acesso ao mesmo
            3. Definir a gama de mensagens
            4. Compilar preferências de etiquetagem"""),

        "ru": inspect.cleandoc("""
            📊 Хорошо, давайте соберем статистику канала. Для этого мы пройдем <b>следующие 4 шага:</b>
        
            1. Выберем канал
            2. Проверим к нему доступ
            3. Определим диапазон сообщений
            4. Составим предпочтения по тегам"""),

        "zh": inspect.cleandoc("""
            📊 好了，让我们收集渠道的统计数据。要做到这一点，我们将通过以<b>下4个步骤。</b>

            1. 选择一个频道
            2. 检查对它的访问
            3. 定义信息的范围
            4. 编制标签偏好""")
    },
    "getstats-steps-button":
    {
        "en": "✨ Let's do it!",
        "es": "✨ ¡Vamos a hacerlo!",
        "fr": "✨ C'est parti !",
        "pt": "✨ Vamos a isso!",
        "ru": "✨ Приступим!",
        "zh": "✨ 让我们行动起来吧!"
    },
    "getstats-link":
    {
        "en": "[ 1 ] : Send link to the channel",
        "es": "[ 1 ] : Enviar el enlace al canal",
        "fr": "[ 1 ] : Envoyer le lien vers le canal",
        "pt": "[ 1 ] : Enviar link para o canal",
        "ru": "[ 1 ] : Отправьте ссылку на канал",
        "zh": "[ 1 ] : 发送链接到频道"
    },
    "getstats-link-error":
    {
        "en": "Not a channel link",
        "es": "No es un enlace de canal",
        "fr": "Pas un lien de canal",
        "pt": "Não é uma ligação de canal",
        "ru": "Не является ссылкой канала",
        "zh": "不是通道链接"
    },
    "getstats-permission":
    {
        "en": "[ 2 ] : The channel is private, add a bot to it",
        "es": "[ 2 ] : El canal es privado, añade un bot a él",
        "fr": "[ 2 ] : Le canal est privé, ajoutez-y un bot",
        "pt": "[ 2 ] : O canal é privado, acrescente-lhe um bot",
        "ru": "[ 2 ] : Канал приватный, добавьте в него бота",
        "zh": "[ 2 ] ：该频道是私人频道，添加一个机器人到该频道。"
    },
    "getstats-permission-button":
    {
        "en": "✅ Done",
        "es": "✅ Fabricado por",
        "fr": "✅ Terminé",
        "pt": "✅ Feito",
        "ru": "✅ Сделано",
        "zh": "✅ 已完成"
    },
    "getstats-permission-forward":
    {
        "en": inspect.cleandoc("""
            Okay, forward any message from your channel
        
            If the message is not forwarded on behalf of your channel, send a link to it"""),

        "es": inspect.cleandoc("""
            Ok, reenviar cualquier mensaje de su canal
        
            Si el mensaje no se reenvía en nombre de su canal, envíe un enlace al mismo"""),

        "fr": inspect.cleandoc("""
            Ok, transférez n'importe quel message de votre canal

            Si le message n'est pas transféré au nom de votre canal, envoyez un lien vers ce message"""),

        "pt": inspect.cleandoc("""
            Ok, encaminhe qualquer mensagem do seu canal

            Se a mensagem não for enviada em nome do seu canal, envie um link para o mesmo"""),

        "ru": inspect.cleandoc("""
            Хорошо, перешлите любое сообщение из вашего канала
        
            Если сообщение не пересылается от имени вашего канала, отправьте ссылку на него"""),

        "zh": inspect.cleandoc("""
            好的，转发任何来自你的频道的信息

            如果该信息不是代表你的频道转发的，请发送一个链接给它""")
    },
    "getstats-permission-error":
    {
        "en": "<b>[ Access error ] : </b>Forward message from the channel you added bot to",
        "es": "<b>[ Error de acceso ] : </b>Reenvía el mensaje desde el canal al que has añadido el bot",
        "fr": "<b>[ Erreur d'accès ] : </b>Transférer le message du canal auquel vous avez ajouté le bot",
        "pt": "<b>[ Erro de acesso ] : </b>Encaminhar mensagem do canal a que acrescentou bot",
        "ru": "<b>[ Ошибка доступа ] : </b>Перешлите сообщение из канала, в который вы добавили бота",
        "zh": "<b>[ 访问错误 ] : </b>转发来自你添加机器人的频道的信息"
    },
    "getstats-message-range-start":
    {
        "en": inspect.cleandoc("\
            [ 3 ] : Let's define the range of messages that will be counted in the statistics. "\
            "Forward the message which will be the beginning of the range or use the default value"\
            """
        
            If the message is not forwarded on behalf of your channel, send a link to it"""),

        "es": inspect.cleandoc("\
            [ 3 ] : Definamos el rango de mensajes que se contabilizarán en las estadísticas. "\
            "Reenvíe el mensaje que será el inicio del rango o utilice el valor por defecto"\
            """
        
            Si el mensaje no se reenvía en nombre de su canal, envíe un enlace al mismo"""),

        "fr": inspect.cleandoc("\
            [ 3 ] : Définissons la plage de messages qui seront comptabilisés dans les statistiques. "\
            "Faites suivre le message qui sera le début de la plage ou utilisez la valeur par défaut"\
            """
        
            Si le message n'est pas transféré au nom de votre canal, envoyez un lien vers celui-ci"""),

        "pt": inspect.cleandoc("\
            [ 3 ] : Vamos definir o intervalo de mensagens que serão contadas nas estatísticas. "\
            "Encaminhar a mensagem que será o início do intervalo ou utilizar o valor por defeito"\
            """
        
            Se a mensagem não for enviada em nome do seu canal, envie um link para o mesmo"""),

        "ru": inspect.cleandoc("\
            [ 3 ] : Давайте определим диапазон сообщений, которые будут учитываться в статистике. "\
            "Перешлите сообщение, которое будет началом промежутка или используйте значение по умолчанию"\
            """
        
            Если сообщение не пересылается от имени вашего канала, отправьте ссылку на него"""),

        "zh": inspect.cleandoc("\
            [ 3 ] ：让我们定义将被计入统计的信息范围。 "\
            "转发将是该范围的开始的消息或使用默认值"\
            """
        
            如果该消息不是代表你的频道转发的，请发送一个链接。""")
    },
    "getstats-range-start-default-button":
    {
        "en": "From the first message",
        "es": "Del primer mensaje",
        "fr": "Extrait du premier message",
        "pt": "Desde a primeira mensagem",
        "ru": "С первого сообщения",
        "zh": "从第一条信息来看"
    },
    "getstats-message-range-end":
    {
        "en": inspect.cleandoc("""
            Forward the last message, which will be counted in the statistics
        
            If the message is not forwarded on behalf of your channel, send a link to it"""),

        "es": inspect.cleandoc("""
            Reenviar el último mensaje, que se contabilizará en las estadísticas
        
            Si el mensaje no se reenvía en nombre de su canal, envíe un enlace al mismo"""),

        "fr": inspect.cleandoc("""
            Transférer le dernier message, qui sera comptabilisé dans les statistiques

            Si le message n'est pas transféré au nom de votre canal, envoyez un lien vers celui-ci"""),

        "pt": inspect.cleandoc("""
            Encaminhar a última mensagem, que será contada nas estatísticas

            Se a mensagem não for enviada em nome do seu canal, envie um link para o mesmo"""),

        "ru": inspect.cleandoc("""
            Перешлите последнее сообщение, которое будет учитываться в статистике
        
            Если сообщение не пересылается от имени вашего канала, отправьте ссылку на него"""),

        "zh": inspect.cleandoc("""
            转发最后一条信息，这将被计入统计中

            如果消息没有代表你的频道转发，请发送一个链接给它""")
    },
    "getstats-message-range-end-error":
    {
        "en": "The last message cannot be after the first",
        "es": "El último mensaje no puede ser posterior al primero",
        "fr": "Le dernier message ne peut pas se trouver après le premier",
        "pt": "A última mensagem não pode ser depois da primeira",
        "ru": "Последнее сообщение не может быть после первого",
        "zh": "最后一条信息不能在第一条之后"
    },
    "getstats-message-range-error":
    {
        "en": "Not the message of the selected channel",
        "es": "No es el mensaje del canal seleccionado",
        "fr": "Pas le message de la chaîne sélectionnée",
        "pt": "Não a mensagem do canal seleccionado",
        "ru": "Не является сообщением выбранного канала",
        "zh": "不是所选频道的信息"
    },
    "getstats-tags-preferences":
    {
        "en": inspect.cleandoc("\
            [ 4 ] : Let's set up tagging preferences, you have a choice of <b>3 options</b>. "\
            "This affects which tags will be displayed in the statistics:"\
            """

            • <b>Skip</b> – all tags found
            • <b>Include</b> – only the tags you select
            • <b>Exclude</b> – all tags except the ones you specify"""),

        "es": inspect.cleandoc("\
            [ 4 ] : Vamos a configurar las preferencias de etiquetado, usted puede elegir entre <b>3 opciones</b>. "\
            "Esto afecta a las etiquetas que se mostrarán en las estadísticas:"\
            """
        
            • <b>Omitir</b> – todas las etiquetas encontradas
            • <b>Incluir</b> – sólo las etiquetas que usted seleccione
            • <b>Excluir</b> – todas las etiquetas excepto las que usted especifique"""),

        "fr": inspect.cleandoc("\
            [ 4 ] : Configurons les préférences de marquage, vous avez le choix entre 3 options. "\
            "Ceci affecte les tags qui seront affichés dans les statistiques:"\
            """
        
            • <b>Skip</b> – tous les tags trouvés
            • <b>Inclure</b> – uniquement les balises que vous sélectionnez
            • <b>Exclure</b> – tous les tags sauf ceux que vous spécifiez"""),

        "pt": inspect.cleandoc("\
            [ 4 ] : Vamos estabelecer preferências de marcação, tem 3 opções à sua escolha. "\
            "Isto afecta quais as etiquetas que serão exibidas nas estatísticas:"\
            """
        
            • <b>Saltar</b> – todas as etiquetas encontradas
            • <b>Inclua</b> – apenas as etiquetas que seleccionar
            • <b>Excluir</b> – todas as etiquetas excepto as que especificar"""),

        "ru": inspect.cleandoc("\
            [ 4 ] : Настроим предпочтения по тегам, у вас есть выбор из <b>3 опций</b>. "\
            "Это влияет на то, какие теги будут отображаться в статистике:"\
            """
        
            • <b>Пропустить</b> – все найденные теги
            • <b>Включить</b> – только выбранные вами теги
            • <b>Исключить</b> – все теги, кроме указанных вами"""),

        "zh": inspect.cleandoc("\
            [ 4 ]：让我们来设置标签偏好，你可以选择<b>3个选项。</b> "\
            "这将影响哪些标签将被显示在统计中。"\
            """
        
            • <b>跳过</b> – 找到的所有标签
            • <b>包括</b> – 只包括你选择的标签
            • <b>排除</b> – 除了你指定的标签以外的所有标签""")
    },
    "getstats-tags-preferences-buttons":
    {
        "en": ("Skip", "Include", "Exclude"),
        "es": ("Saltar", "Incluya", "Excluya"),
        "fr": ("Skip", "Inclure", "Exclure"),
        "pt": ("Saltar", "Incluir", "Excluir"),
        "ru": ("Пропустить", "Включить", "Исключить"),
        "zh": ("跳过", "包括在内", "不包括")
    },
    "getstats-tags-preferences-include":
    {
        "en": "Send tags to be included in the statistics in the following format: tag1 tag2 tag3 ...",
        "es": "Envíe las etiquetas que se incluirán en las estadísticas en el siguiente formato: tag1 tag2 tag3 ...",
        "fr": "Envoyez les tags à inclure dans les statistiques au format suivant: tag1 tag2 tag3 ...",
        "pt": "Enviar tags para serem incluídas nas estatísticas no seguinte formato: tag1 tag2 tag3 ...",
        "ru": "Отправьте теги для включения в статистику в следующем формате: тег1 тег2 тег3 ...",
        "zh": "以下列格式发送要纳入统计的标签: tag1 tag2 tag3 ..."
    },
    "getstats-tags-preferences-exclude":
    {
        "en": "Send tags to be excluded from statistics in the following format: tag1 tag2 tag3 ...",
        "es": "Envíe las etiquetas que deben excluirse de las estadísticas en el siguiente formato: tag1 tag2 tag3 ...",
        "fr": "Envoyer les tags à exclure des statistiques au format suivant: tag1 tag2 tag3 ...",
        "pt": "Enviar tags para serem excluídas das estatísticas no seguinte formato: tag1 tag2 tag3 ...",
        "ru": "Отправьте теги для исключения из статистики в следующем формате: тег1 тег2 тег3 ...",
        "zh": "以下列格式发送要从统计中排除的标签: tag1 tag2 tag3 ..."
    },
    "getstats-args-saved":
    {
        "en": "Your settings have been saved",
        "es": "Su configuración ha sido guardada",
        "fr": "Vos paramètres ont été enregistrés",
        "pt": "As suas definições foram guardadas",
        "ru": "Ваши параметры сохранены",
        "zh": "您的设置已被保存"
    },
    "getstats-preprocessing":
    {
        "en": "<b>Processing : </b>Progress bar will appear in seconds",
        "es": "<b>Procesamiento : </b>La barra de progreso aparecerá en segundos",
        "fr": "<b>Traitement : </b>la barre de progression apparaîtra en secondes",
        "pt": "<b>Processamento : </b>A barra de progresso aparecerá em segundos",
        "ru": "<b>Обработка : </b>Индикатор выполнения появится через несколько секунд",
        "zh": "<b>处理 : </b>进度条将以秒为单位显示"
    },
    "getstats-processing-prefix":
    {
        "en": "<b>Processing : </b>",
        "es": "<b>Procesamiento : </b>",
        "fr": "<b>Traitement : </b>",
        "pt": "<b>Processamento : </b>",
        "ru": "<b>Обработка : </b>",
        "zh": "<b>处理 : </b>"
    },
    "getstats-processing-access-error":
    {
        "en": "<b>[ Access error ] : </b>Bot was removed from the channel while executing the command",
        "es": "<b>[ Error de acceso ] : </b>El bot se eliminó del canal mientras se ejecutaba el comando",
        "fr": "<b>[ Erreur d'accès ] : </b>Le bot a été retiré du canal pendant l'exécution de la commande",
        "pt": "<b>[ Erro de acesso ] : </b>Bot foi removido do canal durante a execução do comando",
        "ru": "<b>[ Ошибка доступа ] : </b>Бот был удален из канала во время выполнения команды",
        "zh": "<b>[ 访问错误 ] : </b>在执行命令时，机器人被从通道中移除"
    },
    "getstats-processing-flood-error":
    {
        "en": "<b>[ Long wait ] : </b>Unable to get response from Telegram servers, please try again later",
        "es": "<b>[ Larga espera ] : </b>No se puede obtener respuesta de los servidores de Telegram, intente nuevamente más tarde",
        "fr": "<b>[ Longue attente ] : </b>Impossible d'obtenir une réponse des serveurs Telegram, veuillez réessayer plus tard",
        "pt": "<b>[ Longa espera ] : </b>Incapaz de obter resposta dos servidores de telegramas, por favor tente novamente mais tarde",
        "ru": "<b>[ Долгое ожидание ] : </b>Не удается получить ответ от серверов Telegram, попробуйте позже",
        "zh": "<b>[ 漫长的等待 ] : </b>无法从Telegram服务器获得响应，请稍后再试。"
    },
    "getstats-processing-result":
    {
        "en": inspect.cleandoc("""
            📊 <b>Channel «{}»</b>
            => [ {} – {} ]
            number of posts {} <i>({})</i>"""),

        "es": inspect.cleandoc("""
            📊 <b>Canal «{}»</b>
            => [ {} – {} ]
            número de mensajes {} <i>({})</i>"""),

        "fr": inspect.cleandoc("""
            📊 <b>Canal «{}»</b>
            => [ {} – {} ]
            nombre de messages {} <i>({})</i>"""),

        "pt": inspect.cleandoc("""
            📊 <b>Canal «{}»</b>
            => [ {} – {} ]
            número de postos {} <i>({})</i>"""),

        "ru": inspect.cleandoc("""
            📊 <b>Канал «{}»</b>
            => [ {} – {} ]
            количество публикаций {} <i>({})</i>"""),

        "zh": inspect.cleandoc("""
            📊 <b>频道 «{}»</b>
            => [ {} – {} ]
            帖子数量 {} <i>({})</i>""")
    },
    "getstats-processing-result-in-channel":
    {
        "en": inspect.cleandoc("""
            📊 <b>Statistics:</b>
            first post ({})
            number of posts in the channel {} <i>({})</i>"""),

        "es": inspect.cleandoc("""
            📊 <b>Estadísticas:</b>
            primer mensaje ({})
            número de mensajes en el canal {} <i>({})</i>"""),

        "fr": inspect.cleandoc("""
            📊 <b>Statistiques:</b>
            premier message ({})
            nombre de messages dans le canal {} <i>({})</i>"""),

        "pt": inspect.cleandoc("""
            📊 <b>Estatísticas:</b>
            primeiro posto ({})
            número de postos no canal {} <i>({})</i>"""),

        "ru": inspect.cleandoc("""
            📊 <b>Статистика:</b>
            первая публикация ({})
            количество публикаций в канале {} <i>({})</i>"""),

        "zh": inspect.cleandoc("""
            📊 <b>统计数据:</b>
            第一个帖子 ({})
            频道中的帖子数 {} <i>({})</i>""")
    },
    "getstats-processing-result-no-tags":
    {
        "en": "no tags found",
        "es": "no se encontraron hashtags",
        "fr": "aucun tag trouvé",
        "pt": "não foram encontradas etiquetas",
        "ru": "теги не найдены",
        "zh": "没有找到标签"
    }
}


localesButtonGroup = {
    "getstats-range-default": (button for button in locales["getstats-range-start-default-button"].values()),
    "getstats-tags-skip": (buttons[0] for buttons in locales["getstats-tags-preferences-buttons"].values()),
    "getstats-tags-include": (buttons[1] for buttons in locales["getstats-tags-preferences-buttons"].values()),
    "getstats-tags-exclude": (buttons[2] for buttons in locales["getstats-tags-preferences-buttons"].values())
}
