    token_receive = request.cookies.get('mytoken')
    uid = validate_token(token_receive)
    partys, host_party, participant_party = [], [], []
    if uid == False :
        return redirect('/')
    
    result = list(db.party.find({}))
    for r in result:
        if uid == r['host']:
            host_party.append(r)
        elif uid in r['participant']:
            participant_party.append(r)
        elif r['state'] == '0':
            partys.append(r)

    return render_template('home.html', partys = partys, host_party = host_party, participant_party = participant_party)