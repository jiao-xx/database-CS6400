import sys, os
from flask import Flask
from flask import Flask, render_template, request, session, flash, redirect
from flaskext.mysql import MySQL
from flask_session import Session
from wtforms.validators import InputRequired, Length
from dotenv import load_dotenv

import app_constants    # HOUSEHOLD_TYPES, HEATING_COOLING_TYPES, PUBLIC_UTILITY_TYPES, etc.

from HouseholdForm import HouseholdForm
from ApplianceForm import AirhandlerForm
from ApplianceForm import WaterHeaterForm
from PowerForm import PowerForm
from HouseHoldAvgRadiusForm import HouseHoldAvgRadiusForm
from ManufacturerModelSearchForm import ManufacturerModelSearchForm

from HouseholdFormHelper import HouseholdFormHelper
from ApplianceFormHelper import ApplianceFormHelper
from ReportHelper import ReportHelper
from AppHelper import AppHelper
from ImportHelper import ImportHelper

app = Flask(__name__)
mysql = MySQL()
load_dotenv()

# flask session
# https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/#
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '9f5216f9ae274340632f12abe6a43e10397bbb01'
Session(app)

# MySQL configurations 
app.config['MYSQL_DATABASE_USER'] = os.getenv('CS6400_DB_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('CS6400_DB_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('CS6400_DB_NAME')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('CS6400_DB_HOST')
app.config['MYSQL_DATABASE_PORT'] = int(os.getenv('CS6400_DB_PORT'))

mysql.init_app(app)

ERROR_MESSAGE='danger'
SUCCESS_MESSAGE ='success'
WARNING_MESSAGE ='warning'

@app.route("/test")
def test():

    results = ReportHelper.manufacturer_model_search(mysql, "Sony")
    print('query results: ')
    print(results, file=sys.stdout)
    return redirect("/appliance")

@app.route("/")
def main():

    return render_template('index.html')

## Household
@app.route("/household", methods = ['POST', 'GET'])
def household():

    form = HouseholdForm()

    if form.validate_on_submit():

        is_email_available = AppHelper.is_email_available(mysql, form.email.data)
        is_postalcode_valid = AppHelper.is_postalcode_valid(mysql, form.postalCode.data)

        # check if the email is available (not already in the db)
        if is_email_available != True:
            flash('The email address you entered is not available.', ERROR_MESSAGE)
            return render_template('household.html', form=form)

        if is_postalcode_valid != True:
            flash('The postal code that you entered is not in our database.', ERROR_MESSAGE)
            return render_template('household.html', form=form)

        if not form.heatingSetting.data and not form.checkNoHeat.data:
            flash("The 'Thermostat setting for heating' is required. If you do not have heating please select the 'No heat' check box.", ERROR_MESSAGE)

            return render_template('household.html', form=form)

        if not form.coolingSetting.data and not form.checkNoCooling.data:
            flash("The 'Thermostat setting for cooling' is required. If you do not have cooling please select the 'No heat' check box.", ERROR_MESSAGE)
            
            return render_template('household.html', form=form)

        # add the household
        HouseholdFormHelper.insert_household(mysql,
            form.email.data,
            form.squareFootage.data,
            form.householdType.data,
            form.heatingSetting.data,
            form.coolingSetting.data,
            form.postalCode.data
        )

        # get the household ID
        householdID = HouseholdFormHelper.get_household_id(mysql, form.email.data)
        session["householdID"] = householdID

        # add the utilities if any are selected
        if form.publicUtilities.data:
            HouseholdFormHelper.insert_household_utilities(mysql, householdID, form.publicUtilities.data)

        print('household(): ')
        print(form.publicUtilities.data, file=sys.stdout)
        print(f'householdID: {householdID}', file=sys.stdout)
        flash('Your household data was successfully entered.', SUCCESS_MESSAGE)

        return redirect("/appliance")
    else:

        return render_template('household.html', form=form)

## Appliance
@app.route("/appliance", methods = ['POST', 'GET'])
def appliance():

    airhandlerForm = AirhandlerForm()
    waterheaterForm = WaterHeaterForm()

    if not check_session():
        return redirect("/household")

    householdID = session["householdID"]

    if airhandlerForm.validate_on_submit():

        airhandlerErrors = False
        errorMessage = ''

        if 'Air conditioner' in airhandlerForm.heatingCoolingTypes.data:
            if not airhandlerForm.eer.data:
                flash("If you select 'Air conditioner', you must enter the Energy efficiency ratio.", ERROR_MESSAGE)

                return render_template('appliance.html',airhandlerForm=airhandlerForm, waterheaterForm=waterheaterForm)
        
        if 'Heater' in airhandlerForm.heatingCoolingTypes.data:
            if not airhandlerForm.heaterEnergySource.data:
                flash("If you select 'Heater', you must select the Energy source.", ERROR_MESSAGE)        
                return render_template('appliance.html',airhandlerForm=airhandlerForm, waterheaterForm=waterheaterForm)
            
        if 'Heat pump' in airhandlerForm.heatingCoolingTypes.data:
            if not airhandlerForm.seer.data or not airhandlerForm.hspf.data :
                flash("If you select 'Heat pump', you must enter both the SEER and HSPF values.", ERROR_MESSAGE)  
                return render_template('appliance.html',airhandlerForm=airhandlerForm, waterheaterForm=waterheaterForm)

        print(airhandlerForm.heatingCoolingTypes.data, file=sys.stdout)   
        # add the air handler
        ApplianceFormHelper.insert_air_handler(mysql, 
                                               householdID, 
                                               airhandlerForm.ahManufacturer.data, 
                                               airhandlerForm.ahBtus.data, 
                                               airhandlerForm.ahModelName.data, 
                                               airhandlerForm.fanRpms.data, 
                                               airhandlerForm.eer.data, 
                                               airhandlerForm.heaterEnergySource.data,
                                               airhandlerForm.seer.data,
                                               airhandlerForm.hspf.data,
                                               airhandlerForm.heatingCoolingTypes.data)
        return redirect("/appliance-list")
    
    elif waterheaterForm.validate_on_submit():

        # add the water heater
        ApplianceFormHelper.insert_water_heater(mysql, 
                                                householdID, 
                                                waterheaterForm.whManufacturer.data, 
                                                waterheaterForm.whBtus.data, 
                                                waterheaterForm.whModelName.data, 
                                                waterheaterForm.waterHeaterEnergySource.data, 
                                                waterheaterForm.tankSize.data, 
                                                waterheaterForm.currentTempSetting.data)

        

        return redirect("/appliance-list")
    else:

        manufacturers = [item[0] for item in ApplianceFormHelper.get_manufacturers(mysql)]
        airhandlerForm.ahManufacturer.choices = manufacturers
        waterheaterForm.whManufacturer.choices = manufacturers
        return render_template('appliance.html',airhandlerForm=airhandlerForm, waterheaterForm=waterheaterForm)

## Appliance List
@app.route("/appliance-list", methods = ['GET'])
def appliance_list():

    if not check_session():
        return redirect("/household")
    
    householdID = session.get("householdID")
    household_appliances = ApplianceFormHelper.get_household_appliances(mysql, householdID)
    return render_template('appliance-list.html', results=household_appliances)

## Appliance Delete
@app.route("/appliance-list/<id>", methods = ['POST'])
def appliance_delete(id):

    if not check_session():
        return redirect("/household")
    
    print(f'appliance_delete: {id}', file=sys.stdout) 

    if ApplianceFormHelper.delete_appliance(mysql, id):
        flash("The appliance has been deleted.", SUCCESS_MESSAGE) 
    else:
        flash(app_constants.MESSAGE_UNEXPECTED_ERROR, ERROR_MESSAGE) 

    return redirect("/appliance-list")

@app.route("/power", methods = ['POST', 'GET'])
def power():

    if not check_session():
        return redirect("/household")
    
    householdID = session.get("householdID")
    can_skip = can_skip_power_generation(householdID)

    form = PowerForm()  

    if request.form and request.form['action'] == 'skip':
        if can_skip:
            return redirect("/power-list")
    
    if form.validate_on_submit():

        AppHelper.insert_power_generator(mysql,
            householdID,   
            form.avgKwh.data,
            form.batteryStorageCapacity.data,
            form.powerGenerationType.data
        )

        return redirect("/power-list")
            
    return render_template('power.html', can_skip=can_skip, form=form)

@app.route("/power-list")
def power_list():

    if not check_session():
        return redirect("/household")
    
    householdID = session.get("householdID")
    
    can_skip = can_skip_power_generation(householdID)

    if not can_skip:
        flash(app_constants.MESSAGE_OTG_NO_POWER, WARNING_MESSAGE) 

    power_generators = AppHelper.get_household_power_generation(mysql, householdID)
    return render_template('power-list.html', results=power_generators, can_skip=can_skip)

## Power generator delete
@app.route("/power-list/<id>", methods = ['POST'])
def power_generator_delete(id):

    if not check_session():
        return redirect("/household")
    
    print(f'power_delete: {id}', file=sys.stdout) 

    if AppHelper.delete_power_generator(mysql, id):

        can_skip = can_skip_power_generation(session.get("householdID"))

        if not can_skip:
            flash(app_constants.MESSAGE_POWER_GENERATOR_DELETED + ' ' + app_constants.MESSAGE_OTG_NO_POWER, WARNING_MESSAGE) 
        else:
            flash(app_constants.MESSAGE_POWER_GENERATOR_DELETED, SUCCESS_MESSAGE) 
    else:
        flash(app_constants.MESSAGE_UNEXPECTED_ERROR, ERROR_MESSAGE) 

    return redirect("/power-list")

@app.route("/done")
def done():
    return render_template('done.html')

# REPORTS
@app.route("/report")
def reports():
    return render_template('report.html')

@app.route("/report/top-manufacturers")
def report_top_manufacturers():

    results = ReportHelper.get_top_manufacturers(mysql)
    return render_template('report-top-manufacturers.html', results = results, isDrillDown=False)

@app.route('/report/top-manufacturers/<manufacturerName>')
def report_top_manufacturers_drilldown(manufacturerName):

    results = results = ReportHelper.get_top_manufacturers_drilldown(mysql, manufacturerName)
    return render_template('report-top-manufacturers.html', results = results, isDrillDown=True, subPageTitle=manufacturerName)

@app.route("/report/manufacturer-model-search", methods = ['POST', 'GET'])
def report_manufacturer_model_search():

    form = ManufacturerModelSearchForm()

    if form.validate_on_submit():
        
        results = ReportHelper.manufacturer_model_search(mysql, form.searchTerm.data)

        
        return render_template('report-manufacturer-model-search.html', form=form, results=results)
    else:
        return render_template('report-manufacturer-model-search.html', form=form)
    

@app.route("/report/hc-method-details")
def report_heating_cooling_methods():

    result1, result2, result3 = ReportHelper.get_heating_cooling_methods(mysql)  

    #print(f'report_heating_cooling_methods: {results}', file=sys.stdout) 
    return render_template('report-hc-details.html',result1=result1,result2=result2,result3=result3)

@app.route("/report/waterheater-statistics")
def report_waterheater_statistics():
    
    results = ReportHelper.get_waterheater_statistics(mysql)  
    return render_template('report-waterheater-statistics.html',results = results, isDrillDown=False)

@app.route("/report/waterheater-statistics/<state>")
def report_waterheater_statistics_drilldown(state):
    
    results = ReportHelper.get_waterheater_statistics_drilldown(mysql, state)  
    return render_template('report-waterheater-statistics.html',results = results, isDrillDown=True, subPageTitle=state)

@app.route("/report/otg-household-dashboard")
def report_otg_household_dashboard():
    
    result1, result2, result3, result4, result5, result6  = ReportHelper.get_otg_household_dashboard(mysql)  
    return render_template('report-otg-household-dashboard.html',
                           result1=result1, result2=result2, result3=result3, 
                           result4=result4, result5=result5, result6=result6)

@app.route("/report/household-avg-radius", methods = ['POST', 'GET'])
def report_household_avg_radius():

    results = []
    household_avgs = []
    household_type_count = []
    form = HouseHoldAvgRadiusForm()

    if form.validate_on_submit():

        is_postalcode_valid = AppHelper.is_postalcode_valid(mysql, form.postalCode.data)

        print(f'is_postalcode_valid: {is_postalcode_valid}', file=sys.stdout) 

        if is_postalcode_valid != True:
            flash('The postal code that you entered is not in our database.', ERROR_MESSAGE)
            return render_template('report-household-avg-radius.html', results = results, form=form)

        results, household_type_count, household_avgs, household_avg_power = ReportHelper.get_household_avg_radius(mysql,
            form.postalCode.data,
            form.searchRadius.data
        )

        #print(results, file=sys.stdout)
        return render_template('report-household-avg-radius.html', results=results, household_avgs=household_avgs,household_type_count=household_type_count,
                               household_avg_power=household_avg_power,form=form)
    else:
        return render_template('report-household-avg-radius.html', form=form)


def check_session():
    if not session.get("householdID"):
        flash("We are unable determine your household. Please register your household to continue.", ERROR_MESSAGE)
        return False
    else:
        return True

def can_skip_power_generation(householdID):
    is_off_the_grid = AppHelper.is_household_otg(mysql, householdID)
    household_has_power = AppHelper.household_has_power_generators(mysql, householdID)

    can_skip = True if (household_has_power or is_off_the_grid==False) else False

    print(f'is_off_the_grid: {is_off_the_grid}', file=sys.stdout) 
    print(f'can_skip: {can_skip}', file=sys.stdout)

    return can_skip

@app.route("/import")
def import_():

    #ImportError.import_household(mysql, '/Users/corey/Desktop/_gatech/Demo Data/Household.tsv')
    #ImportHelper.import_power(mysql, '/Users/corey/Desktop/_gatech/Demo Data/Power.tsv')
    #ImportHelper.import_appliance(mysql, '/Users/corey/Desktop/_gatech/Demo Data/Appliance.tsv')

    flash('The data has been imported.', SUCCESS_MESSAGE)
    return redirect("/")

if __name__ == "__main__":
    app.run()