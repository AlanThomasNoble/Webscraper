from bs4 import BeautifulSoup
import requests
import json

url = 'https://www.futurelearn.com/courses?filter_category=open&filter_course_type=open&filter_availability=open&all_courses=1'
response = requests.get(url, timeout=5)
content = BeautifulSoup(response.content, "html.parser")

courses = []

# Go through all the courses on the all courses page
for course in content.findAll('div', attrs={"class": "m-card Container-wrapper_GWW4X Container-grey_3ORsI"}):

    # Get the link to each source and follow the link
    link = course.find('a', attrs={"class": "link-wrapper_3VSCt link-withFlexGrow_2V4h9"}).get('href')
    concat_link = "https://www.futurelearn.com" + link
    response_2 = requests.get(concat_link, timeout=5)
    link_content = BeautifulSoup(response_2.content, "html.parser")

    # Information for each course. Fault tolerance was prioritized.
    # Course Name
    title = link_content.find('h1', attrs={"class": "m-dual-billboard__heading"})
    if title == None:
        title = ''
    else:    
        title = title.text

    # Category
    category = link_content.find('div', attrs={"class": "a-item-title"})
    if category == None:
        category = ''
    else:
        category = category.text.replace("Courses / ", "")

    # Short description
    short_description = link_content.find('p', attrs={"class": "m-dual-billboard__message"})
    if short_description == None:
        short_description = ''
    else:
        short_description = short_description.text.replace("\xa0", " ")

    # Detailed description
    detailed_description = link_content.find('div', attrs={"id": "course-outline"})
    if detailed_description == None:
        detailed_description = ''
    else:
        detailed_description = detailed_description.text
        detailed_description = detailed_description.replace("Read more", "").replace("\xa0", " ").replace("\n\n", " ").replace("\n", " ")
        detailed_description = detailed_description.lstrip().rstrip()

    # Mentors
    test_mentor = link_content.find('header', attrs={"class": "m-info-block__header m-info-block__header--double"})
    if test_mentor == None:
        mentors = []
    else:
        mentors = []
        for each_mentor in link_content.find_all('header', attrs={"class": "m-info-block__header m-info-block__header--double"}):
            mentors.append(each_mentor.text)


    total_num = len(link_content.find_all("span",{"class":"m-key-info__content"})) # fault tolerance checks below
    # Duration
    if total_num >= 1:
        duration = link_content.find_all("span",{"class":"m-key-info__content"})[0].text
    else:
        duration = ''

    # Weekly study hours
    if total_num >= 2:
        weekly_study = link_content.find_all("span",{"class":"m-key-info__content"})[1].text.replace('\n', '').replace(' hours', '').replace(' hour', '')
        weekly_study_hours = int(weekly_study)
    else:
        weekly_study_hours = None
    
    # Cost
    if total_num >= 3:
        cost = link_content.find_all("span",{"class":"m-key-info__content"})[2].text.replace('\n', '')
        if '$' in cost:
            cost = int(cost.replace('$', ''))
        else:
            cost = 0
    else:
        cost = None

    # Organization
    class_name = "heading-wrapper_1at_r heading-sBreakpointAlignmentleft_Gh9ud heading-sBreakpointSizelarge_1a0Mj heading-black_6_KIa heading-isRegular_1inPG"
    organization = link_content.find('h2', attrs={"class": class_name})
    if organization == None:
        organization = ''
    else:
        organization = organization.text
    
    # Put the information into a JSON object
    courseDict = {
        "title": title.replace('\n', ''),
        "mentor": mentors,
        "short_description": short_description.replace('\n', ''),
        "detailed_description": detailed_description,
        "duration": duration.replace('\n', ''),
        "weekly_study_hours": weekly_study_hours,
        "cost_USD": cost,
        "category": category.replace('\n', ''),
        "organization": organization,
    }
    courses.append(courseDict)

# Write the JSON data to a new file
with open('courses-json_output.json', 'w') as file_1:
    json.dump(courses, file_1)