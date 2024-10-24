from flask import Flask,request,render_template,jsonify
from newfacefinder import list_of_match_images
app=Flask(__name__)

@app.route('/ok',methods=['GET','POST'])
def index():
    return {"message":"I ma ok!"}
@app.route("/user/<id>",methods=['GET','POST'])
def api(id):
    print(id)
    if request.method=='GET':
        print(id)
        return {'id':id}
    return
@app.route("/facefinder",methods=['GET','POST'])
def facefinder():
    print()
    if request.method=='POST':
        data=request.form
        #file=request.files
        file = request.files.get('image')
        file_path = data.get('path') 
        print(file_path)
        result=list_of_match_images(file_path)
        if result:
            return jsonify({'matching_images': result}), 200
        else:
            return jsonify({'message': 'No matching images found'}), 404
    return "Method Not Allowed", 405  # Handle non-POST requests


if __name__ == "__main__":
    app.run(port=5000,debug=True)