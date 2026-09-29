# main/cgpa_utils.py
GRADE_SCALE = {
    'A': {'min_score': 70, 'max_score': 100, 'point': 5},
    'B': {'min_score': 60, 'max_score': 69, 'point': 4},
    'C': {'min_score': 50, 'max_score': 59, 'point': 3},
    'D': {'min_score': 45, 'max_score': 49, 'point': 2},
    'E': {'min_score': 40, 'max_score': 44, 'point': 1},
    'F': {'min_score': 0, 'max_score': 39, 'point': 0},
}

def get_grade_and_point(score):
    if score < 0 or score > 100:
        return None, None
    for grade, data in GRADE_SCALE.items():
        if data['min_score'] <= score <= data['max_score']:
            return grade, data['point']
    return 'F', 0

def calculate_gpa(courses_data):
    total_units = 0
    total_credit_points = 0
    course_results = []
    
    for course in courses_data:
        credit_unit = course['credit_unit']
        score = course['score']
        
        grade, point = get_grade_and_point(score)
        credit_point = credit_unit * point
        
        course_results.append({
            'code': course.get('code', ''),
            'name': course['name'],
            'credit_unit': credit_unit,
            'score': score,
            'grade': grade,
            'point': point,
            'credit_point': credit_point
        })
        
        total_units += credit_unit
        total_credit_points += credit_point
    
    gpa = total_credit_points / total_units if total_units > 0 else 0
    
    if gpa >= 4.5:
        classification = "First Class"
    elif gpa >= 3.5:
        classification = "Second Class Upper"
    elif gpa >= 2.5:
        classification = "Second Class Lower"
    elif gpa >= 1.5:
        classification = "Third Class"
    else:
        classification = "Pass/Fail"
    
    return {
        'gpa': round(gpa, 2),
        'total_units': total_units,
        'total_credit_points': total_credit_points,
        'classification': classification,
        'course_results': course_results
    }