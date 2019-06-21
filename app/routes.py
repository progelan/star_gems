from app import app, db, login_manager
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Preference, Gem, TypeGem, Requirement
from app.forms import LoginForm, RegistrationForm, EditProfileForm, RemoveProfileForm,\
    RestoreProfileForm, EditPasswordForm, AddGemsForm, ActionById, EditPrefForm, AddPrefForm,\
    ViewQueryForm, DistributionForm, RequirementsForm, GemTypesForm, AddTypeForm
from datetime import datetime, timedelta
from sqlalchemy import text, desc, or_, and_


@login_manager.user_loader# пользовательский загрузчик
def load_user(id):
    return db.session.query(User).get(int(id))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow() + timedelta(hours=5)
        db.session.commit()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:# True, если юзер зареган
        return redirect(url_for('users'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('You are logged in as a {}, {}'.format(user.name, user.character))
        if user.character == 'elf':
            return redirect(url_for('user', username=user.username))
        elif user.character == 'gnome':
            return redirect(url_for('add_gems'))
        elif user.character == 'master':
            return redirect(url_for('gems'))
        else:
            return redirect(url_for('users'))
    return render_template('login.html', title='Sign In', form=form)# form = form передает объект формы


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, character=form.character.data, name=form.username.data.title())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/edit_password', methods=['GET', 'POST'])
@login_required# защищает функцию просмотра: будет доступна только для зарегистрированных пользователей
def edit_password():

    form = EditPasswordForm()
    
    if form.validate_on_submit():
        user = current_user
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your password has been changed.')
        return redirect(url_for('edit_password'))
    return render_template('edit_password.html', title='Edit password', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form_edit = EditProfileForm(current_user.username, current_user.email)
    form_remove = RemoveProfileForm()
    form_restore = RestoreProfileForm()
    
    if request.method == 'GET':
        form_edit.username.data = current_user.username
        form_edit.email.data = current_user.email
        form_edit.name.data = current_user.name
    if form_restore.is_submitted() and form_restore.submit_restore.data:
        current_user.status = True
        db.session.commit()
        flash('Profile has been restored.')
        return redirect(url_for('edit_profile'))
    elif form_remove.is_submitted() and form_remove.submit_remove.data:
        current_user.status = False
        current_user.deletion_date = datetime.utcnow()
        db.session.commit()
        flash('Profile has been deleted.')
        return redirect(url_for('edit_profile'))
    elif form_edit.validate_on_submit():
        current_user.username = form_edit.username.data
        current_user.name = form_edit.name.data
        current_user.email = form_edit.email.data
        db.session.commit()
        flash('Profile has been updated.')
        return redirect(url_for('edit_profile'))
    return render_template('edit_profile.html', title='Edit profile', user=user, form_edit=form_edit, form_remove=form_remove,\
        form_restore=form_restore)


@app.route('/add_gems', methods=['GET', 'POST'])
@login_required
def add_gems():

    form = AddGemsForm()
    temp_message = []

    if request.method == 'GET':
        form.amount_gem.data = 0
    elif form.validate_on_submit():
        for gem in range(int(form.amount_gem.data)):
            gem = Gem(type=str(form.type_gem.data.type), gnome_id=current_user.id)
            db.session.add(gem)
            db.session.commit()
            temp_message.append(gem.type)
        flash('Gem: {} - successfully added to the system.'.format(', '.join(temp_message)))
    return render_template('add_gems.html', title='Adding gems', form=form)


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):

    def get_prefs():# предпочтения эльфа
        return user.preferences.all()

    def get_types_pref():
        return [pref.gem_type for pref in get_prefs()]

    def get_gem_types():
        return [x.type for x in TypeGem.query.all()]

    def get_new_pref():
        return [(gem_type, gem_type) for gem_type in list(set(get_gem_types())-set(get_types_pref()))]

    def get_mined_gems():
        gems_gnome = Gem.query.filter_by(gnome_id=user.id).all()
        list_types = [gem.type for gem in gems_gnome]
        return {gem.type : list_types.count(gem.type) for gem in gems_gnome}

    def get_assigned_gems():
        return Gem.query.filter_by(elf_id=user.id).filter(Gem.status=='assigned').all()

    def get_confirmed_gems():
        gems_elf = Gem.query.filter_by(elf_id=user.id).filter(Gem.status=='confirmed').all()
        list_types = [gem.type for gem in gems_elf]
        return {gem.type : list_types.count(gem.type) for gem in gems_elf}

    
    user = User.query.filter_by(username=username).first_or_404()
    form_confirm = ActionById(prefix='confirm')
    form_add = AddPrefForm()
    form_del = ActionById(prefix='del')
    form_edit = EditPrefForm(prefix='edit')

    form_add.gem_type.choices = get_new_pref()


    form_edit.pref.label = ''
    form_edit.gem_rate.label = 'Rate'

    if form_confirm.is_submitted() and form_confirm.value.data:
        gem = Gem.query.get(form_confirm.value.data)
        gem.status = 'confirmed'
        gem.confirmation_date = datetime.utcnow()
        db.session.add(gem)
        db.session.commit()
        flash('The assigned {} was successfully confirmed by the {}.'.format(gem.type, user.name))
    elif form_del.is_submitted() and form_del.value.data:
        pref_del = Preference.query.get(form_del.value.data)
        db.session.delete(pref_del)
        db.session.commit()
        flash('Preference "{}" successfully deleted.'.format(pref_del))
    elif "gem_type" in request.form and form_add.gem_rate.validate(form_add):
        pref = Preference(gem_type=form_add.gem_type.data, gem_rate=form_add.gem_rate.data, elf_id=user.id)
        db.session.add(pref)
        db.session.commit()
        form_add.gem_type.choices = get_new_pref()
        flash('Preference "{}" successfully added.'.format(pref))
    elif "edit-submit_edit" in request.form and form_edit.gem_rate.validate(form_edit) and form_edit.pref.validate(form_edit):
        elf_pref = form_edit.pref.data
        elf_pref.gem_rate = form_edit.gem_rate.data
        db.session.commit()
        flash('Preference successfully edited.')

    return render_template('user.html',
                            title=user.name,
                            user=user,
                            prefs=get_prefs(),
                            mined_gems=get_mined_gems(),
                            assigned_gems=get_assigned_gems(),
                            confirmed_gems=get_confirmed_gems(),
                            form_confirm=form_confirm,
                            form_add=form_add,
                            form_del=form_del,
                            form_edit=form_edit)


@app.route('/')
@app.route('/users', methods=['GET', 'POST'])
def users():

    form = ActionById()

    form_view = ViewQueryForm()

    def get_elves():
        return User.query.filter(and_(User.character == 'elf', User.status == True)).all()

    def get_all_elves():
        return User.query.filter(User.character == 'elf').all()

    def get_gnomes():
        return User.query.filter(or_(User.character == 'gnome', User.character == 'master')).filter(User.status == True).all()

    def get_all_gnomes():
        return User.query.filter(or_(User.character == 'gnome', User.character == 'master')).all()

    if form_view.is_submitted():
        return render_template('users.html', title='Users', elves=get_all_elves(), gnomes=get_all_gnomes(), form=form, form_view=form_view)

    if form.is_submitted() and form.value.data:
        user = User.query.get(form.value.data)
        user.status = False
        db.session.add(user)
        db.session.commit()
        flash('User successfully removed from the system.')

    return render_template('users.html', title='Users', elves=get_elves(), gnomes=get_gnomes(), form=form, form_view=form_view)


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

    def get_requirements():
        return Requirement.query.all()

    def get_gem_types():
        return TypeGem.query.order_by(TypeGem.type).all()

    form_edit = RequirementsForm(prefix='edit')
    form_gem = GemTypesForm(prefix='gem')
    form_del = ActionById(prefix='del')
    form_add = AddTypeForm(prefix='add')

    if "edit-submit_edit" in request.form and form_edit.req_rate.validate(form_edit) and form_edit.req_type.validate(form_edit):
        req = form_edit.req_type.data
        req.req_rate = form_edit.req_rate.data
        db.session.add(req)
        db.session.commit()
        flash('{} coefficient successfully edited.'.format(req.req_type))
    elif "add-gem_type" in request.form and form_add.validate_on_submit():
        new_type = TypeGem(type=form_add.gem_type.data)
        db.session.add(new_type)
        db.session.commit()
        flash('Type "{}" successfully added to the system.'.format(new_type.type))
    elif form_del.is_submitted() and form_del.value.data:
        type_gem = TypeGem.query.get(form_del.value.data)
        db.session.delete(type_gem)
        db.session.commit()
        flash('Type "{}" has been deleted.'.format(type_gem.type))
    elif "gem-submit_type" in request.form and form_gem.validate_on_submit():
        type_edit = TypeGem.query.filter_by(type=form_gem.gem_type.data.type).first_or_404()
        type_edit.type = form_gem.edit_type.data
        db.session.add(type_edit)
        db.session.commit()
        flash('Type successfully changed to "{}".'.format(type_edit.type))

    return render_template('settings.html',
                           title='settings',
                           form_edit=form_edit,
                           form_del=form_del,
                           form_gem=form_gem,
                           form_add=form_add,
                           reqs=get_requirements(),
                           gem_types=get_gem_types())


@app.route('/gems', methods=['GET', 'POST'])
def gems():

    form = ActionById()
    form_view = ViewQueryForm()

    def get_all_gems():
        return Gem.query.order_by(desc(Gem.mined_date)).all()

    def get_gems():
        return Gem.query.order_by(desc(Gem.mined_date)).filter(Gem.status != 'deleted').all()

    def get_assigned_gems():
        return Gem.query.order_by(desc(Gem.mined_date)).filter(Gem.status == 'assigned').all()

    if form.is_submitted() and form.value.data:
        gem = Gem.query.get(form.value.data)
        gem.status = 'deleted'
        db.session.add(gem)
        db.session.commit()
        flash('Gem successfully removed from the system.')
    elif "view_all_gems" in request.form and form_view.is_submitted():
        return render_template('gems.html', title='Gems', gems=get_all_gems(), form=form, form_view=form_view)
    elif "view_assigned_gems" in request.form and form_view.is_submitted():
        return render_template('gems.html', title='Gems', gems=get_assigned_gems(), form=form, form_view=form_view)

    return render_template('gems.html', title='Gems', gems=get_gems(), form=form, form_view=form_view)



temp_assigned_gems = []

@app.route('/gems_distribution', methods=['GET', 'POST'])
@login_required
def gems_distribution():

    def count_assigned_elf(elf):
        return elf.elf_gems.filter_by(status='assigned').count()

    def count_confirmed_elf(elf):
        return elf.elf_gems.filter_by(status='confirmed').count()

    def get_mined_gems():
        return Gem.query.filter(Gem.status == 'mined').order_by(desc(Gem.mined_date)).all()

    def get_elves():
        return User.query.filter(and_(User.character == 'elf', User.status == True)).all()

    def count_gems_elf(elf):
        return count_assigned_elf(elf) + count_confirmed_elf(elf)

    def sum_gems_elves():
        query = text("SELECT COUNT (id) FROM gem WHERE status='assigned' OR status='confirmed'")
        response = db.engine.execute(query)
        return response.scalar() + num_temp_gems

    def get_weighted_choices():
        return {elf: (count_gems_elf(elf))/sum_gems_elves() for elf in get_elves()}
    
    def hungry_elf():
        return min(get_weighted_choices(), key=get_weighted_choices().get)
    
    form = DistributionForm()

    num_temp_gems = 0
    temp_message = []

    if request.method == 'GET':
        temp_assigned_gems.clear()
    elif form.is_submitted() and form.elf.data:
        gem = Gem.query.get(form.value.data)
        gem.elf = form.elf.data
        gem.status = 'assigned'
        gem.assigned_date = datetime.utcnow()
        gem.master = current_user
        gem.assignation_type = 'hand'
        db.session.add(gem)
        db.session.commit()
        flash('{} successfully assigned to the elf {}.'.format(gem.type, form.elf.data.name))
        return redirect(url_for('gems_distribution'))
    elif "submit_distrib" in request.form:
        if not get_mined_gems():
            flash('No gems for distribution')
        elif not temp_assigned_gems:
            for temp_gem in get_mined_gems():
                temp_gem.elf = hungry_elf()
                temp_gem.status = 'assigned'
                temp_assigned_gems.append(temp_gem)
                num_temp_gems += 1
        else:
            flash('Distribution already done')
        return render_template('gems_distribution.html', title='Gems distribution', gems=temp_assigned_gems, form=form)
    elif "submit_confirm" in request.form:
        if not temp_assigned_gems:
            flash('You first need to make a distribution!')
        else:
            for temp_gem in temp_assigned_gems:
                gem = Gem.query.get(temp_gem.id)
                gem.elf = temp_gem.elf
                gem.status = 'assigned'
                gem.assignation_type = 'algo'
                gem.assigned_date = datetime.utcnow()
                db.session.add(gem)
                db.session.commit()
                temp_message.append(gem.type)
            temp_assigned_gems.clear()
            flash('Distribution successfully completed. Gem: {} - assigned.'.format(', '.join(temp_message)))

    return render_template('gems_distribution.html', title='Gems distribution', gems=get_mined_gems(), form=form)






