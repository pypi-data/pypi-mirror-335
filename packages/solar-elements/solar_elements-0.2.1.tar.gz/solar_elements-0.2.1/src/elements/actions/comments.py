from elements.social import Comment

def comments(element, **details):
    s = session()
    if s is None:
        return abort(401)

    if request.method == "GET":
        comments = Notes.on(element)
        replies = defaultdict(list)
        top_level = []

        last = int(request.query.get('last') or 0)

        for comment in comments.content:
            if comment.author.name == s.member.name or "admin" in s.member.role:
                comment.delete = comment.url
            replying_to = comment.tags.getfirst('e')
            if replying_to is not None:
                replies[replying_to].append(comment)
            else:
                top_level.append(comment)

            responses = Responses.on(comment)
            comment.who = responses.content
            comment.liked = responses.find(s.member.name, 'author') != None

        for comment in top_level:
            comment.replies = replies[comment.url]

            # We need this so we can refer to it in the template
            comment.reply_target = comment.url

        if last:
            top_level = top_level[:-last]
        
        template = Path(tag) / 'components' / 'comments.mo'
        return chevron_template(str(template), **defaults({ 'comments': top_level, 'session': s, 'context': element.url }))

    if request.method == "POST":
        n = Note(**request.forms)
        n.save(path=Path('notes') / element.url)
        n.delete = True

        msg = f'{s.member.display_name} replied to your post.'
        link = f'{root}{ element.url }#{n.name}'
        notify(element.author, content=msg, link=link, notifier=s.member.name)

        template = Path(tag) / 'components' / 'comment.mo'
        return chevron_template(str(template), **defaults({ 'context': element.url, 'session': s  }), scopes=[n])
