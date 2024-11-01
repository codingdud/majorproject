from app import db

class Project(db.Model):
    __tablename__ = 'projects'

    pid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    p_name = db.Column(db.String(255), nullable=False)
    thumb_nail = db.Column(db.Text, default='uploads/placeholder.png')
    
    face_features = db.relationship('FaceFeature', backref='project', lazy=True)
    unique_faces = db.relationship('UniqueFace', backref='project', lazy=True)

    def __repr__(self):
        return f'<Project {self.p_name}>'

    @staticmethod
    def create_project(user_id, p_name, thumb_nail='/default/placeholder.png'):
        new_project = Project(user_id=user_id, p_name=p_name, thumb_nail=thumb_nail)
        db.session.add(new_project)
        db.session.commit()
        return new_project

    @staticmethod
    def get_all_projects():
        return Project.query.all()

    @staticmethod
    def get_project_by_id(pid):
        return Project.query.get(pid)

    @staticmethod
    def update_project(pid, p_name=None, thumb_nail=None):
        project = Project.query.get(pid)
        if project:
            if p_name:
                project.p_name = p_name
            if thumb_nail:
                project.thumb_nail = thumb_nail
            db.session.commit()
            return project
        return None

    @staticmethod
    def delete_project(pid):
        project = Project.query.get(pid)
        if project:
            db.session.delete(project)
            db.session.commit()
            return True
        return False
        
    @staticmethod
    def get_projects_by_user_id(user_id):
        return Project.query.filter_by(user_id=user_id).all()