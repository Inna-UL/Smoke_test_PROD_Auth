*** Settings ***
Documentation	Certification Regression TestSuite
Resource	../../../resource/ApiFunctions.robot
Suite Setup  Link RegressionScheme-Scope-Product1
Suite Teardown  Unlink Scheme Scope    Unlink_ScopeScheme.json

*** Keywords ***
test1 Teardown
	Log To Console	test1a Teardown Beginning
	Expire The Asset	${asset_Id_Product1}
	Log To Console	test1a Teardown Finished

*** Test Cases ***
1a. Setting up Environment
	set global variable	${asset_Id_Product1}

# Asset Part

1. Asset Creation With POST Request
	[Tags]	Functional	asset	create	POST    current
    create product1 asset	CreationOfRegressionProduct1_siscase1.json

2. Search Asset with valid modelName values
	[Tags]	Functional	asset   Search	POST    current
	Search Asset    Asset_Search_with_modelName_exactSearch.json
	Extract asset search response   ${Asset_summary_json}
	should not be equal  ${Asset_total_count}   ${value_as_0}
#	should be equal  ${Asset_offset}    ${value_as_0}
#	should be equal  ${Asset_rows}   ${value_as_400}
    should not be empty  ${Asset_list}
	should be empty  ${Asset_refiners}
	should not be empty  ${Asset_findkeys}
#	should be equal  ${Asset_user}  ${user_1}

2a. Validate Asset Details
    [Tags]	Functional	asset   Search	POST    current
	Extract values from asset list  ${Asset_list}
	list should contain value   ${UL_assetId}   ${asset_Id_Product1}
	list should contain value   ${Asset_Id}   ${asset_Id_Product1}
	Extract values from taxonomy list  ${Asset_taxonomy}
	list should contain value   ${Asset_owner_reference}   ${Asset1_Owner_Ref}

2b. Validate findKeys Details
    [Tags]	Functional	asset   Search	POST    current
    Extract searchParameters from findKeys dictionary    ${Asset_findkeys}
    should not be empty  ${FK_searchParameters_dict}
    Extract modelName values from searchParameters dictionary   ${FK_searchParameters_dict}
    compare lists   ${SP_modelName_values}    ["${model_name_1}_${current_time}", "${exact_search_value}"]

#3. Check Asset State
#	[Tags]	Functional	current
#	${state}=	Get Asset State	${asset_Id_Product1}
#	run keyword if	'${state}' != 'scratchpad'	Fail	test1a Teardown
#	log to console	"Product_State after Standard Assigned To Product": ${state}

4. Edit Asset Model Nomenclature
	[Tags]	Functional	asset	create	POST    current
	Edit Product1 Asset  Edit_ModelNomenclature_RegressionProduct1_siscase1_withCol_ID.json  ${asset_Id_Product1}

5. Get Asset Details
	[Tags]	Functional	asset   create	GET    current
	Details of an Asset  ${asset_Id_Product1}   ContentType=true&user=${user_id}
	${modelNomenclature}    get_values_from_list_of_dictionaries    ${Asset_attributes}    ${modelNomenclature_name}
	should be equal  ${modelNomenclature}   ["Regression_Test_Model_Nomenclature_1_Edit"]

6. Standard Assignment To Product (Product Evaluation Set Up)
	[Tags]	Functional	POST	current
	standard assignment	productnoevalreqd.json	${asset_Id_Product1}

#7. Check Asset State After Associating Standard to Product
#	[Tags]	Functional	current
#	${state}=	Get Asset State	${asset_Id_Product1}
#	run keyword if	'${state}' != 'associated'	Fail	test1a Teardown
#	log to console	"Product_State after Standard Assigned To Product": ${state}

8. Get AssessmentId with Get Standards Associated With an Asset API
	[Tags]	Functional	GET	current
	${assessmentId}  Get AssesmentID	${asset_Id_Product1}
	set global variable	${assessmentId}	${assessmentId}

9. Complete Evaluation
	[Tags]	Functional	POST	current
	Complete Evaluation	markevaluationcomplete.json	${asset_Id_Product1}
	Complete Evaluation	markcollectioncomplete.json	${asset_Id_Product1}

#10. Check Asset State After Evaluation
#	[Tags]	Functional	current
#	${state}=	Get Asset State	${asset_Id_Product1}
#	run keyword if	'${state}' != 'immutable'	Fail	test1a Teardown
#	log to console	"Product_State after Standard Assigned To Product": ${state}


11. Certificate creation
	[Tags]	Functional	certificate	create	POST    current
    create certificate   Certificate/CreationOfRegressionSchemeCertificate.json

12. Link Product and Evaluation to Certificate
    [Tags]	Functional	certificate	create	POST    current
    Get Certificate Transaction Id  ${Certificate_Name}
    ${response}  Get ULAssetID   ${asset_Id_Product1}
    set global variable	${ul_asset_Id}  ${response}
    Link Product to Certificate  Certificate/Link_Product1_Eval1_RegressionCertificate.json

13. Modify Asset Model Nomenclature
	[Tags]	Functional	asset	create	POST    current
	Modify Product1 Asset  Modify_ModelNomenclature_RegressionProduct1_siscase1_withDiffColName.json  ${asset_Id_Product1}

14. Get Asset Details
	[Tags]	Functional	asset   create	GET    current
	Details of an Asset  ${asset_Id_Product12}   ContentType=true&user=${user_id}
	${modelNomenclature}    get_values_from_list_of_dictionaries    ${Asset_attributes}    ${modelNomenclature_name}
	should be equal  ${modelNomenclature}   ["Regression_Test_Model_Nomenclature_1_Modify"]

# Certificate Part



15. Search Certificate with searchParameters as certificateName
	[Tags]	Functional	asset   Search	POST    current
	set global variable  ${operator_value}   ${exact_search_value}
	set global variable  ${search_parameter}  ${certificateName_key}
	set global variable  ${search_parameter_value}   ${Certificate_Name}
	Paginated Search for Certificate    Certificate_Search_with_searchParameters.json
	Extract certificate search response   ${certificate_search}
	should not be empty  ${certificate_total_count}
	should be equal  ${certificate_offset}    ${EMPTY}
	should be equal  ${certificate_rows}   ${EMPTY}
	should not be empty  ${certificate_list}
	should be empty  ${certificate_refiners}
	length should be  ${certificate_findkeys}  ${value_as_1}
#	should be equal  ${Asset_user}  ${user_1}

15a. Validate Certificate Details
    [Tags]	Functional	asset   Search	POST    current
	${certificate_list}  get_dictionary_from_list_of_dictionaries     ${certificate_list}     ${Cert_Owner_Ref}
    Extract values from certificate list  ${certificate_list}
    should be equal  ${is_privateLabel}  [${value_as_false}]
	Compare lists  [${certificate_status}, ${certificate_version}, ${revision_number}, ${certify}]   [["${status_Under_Revision}"], ["${value_as_1.0}"], ["${value_as_0}"], ["${value_as_N}"]]
	compare lists  [${unique_certificateId}, ${CS_certificate_Id}, ${CS_certificate_hierarchyId}, ${CS_partySiteContainerId}]    [["${Certificate_Id}"], ["${Certificate_Id}"], ["${certificate_hierarchy_Id}"], ["${EMPTY}"]]
	compare lists  [${CS_certificate_type}, ${CS_certificate_name}, ${CS_Cerificate_owner_reference}, ${CS_issuing_body}, ${CS_mark}, ${CS_cert_ccn}]    [["${certificate_type_1}"], ["${certificate_name_1}-${current_time}"], ["${Cert_Owner_Ref}"], ["${issuing_body_1}"], ["${mark_1}"], ["${Scope_Code_1}"]]
	compare lists  [${CS_issueDate}, ${CS_revisionDate}, ${CS_withdrawalDate}, ${CS_expiryDate}]     [["${EMPTY}"], ["${EMPTY}"], ["${EMPTY}"], ["${EMPTY}"]]
    should be equal  ${parties}  [[${EMPTY}]]

15b. Validate findKeys searchParameters Details
    [Tags]	Functional	asset   Search	POST    current
    Extract searchParameters from findKeys dictionary    ${certificate_findkeys}
    length should be  ${FK_searchParameters_dict}     ${value_as_1}
    Extract certificateName values from searchParameters dictionary   ${FK_searchParameters_dict}
    compare lists  ${SP_certificateName_values}  ["${Certificate_Name}", "${exact_search_value}"]

16. Edit certificate
    [Tags]	Functional	certificate create	POST    current
    edit certificate  Certificate/EditOfRegressionSchemeCertificate.json    ${Certificate_Id}

17. Certification Mark
    [Tags]	Functional	certificate create	current
    ${Result}   Certificate Mark
    log to console  ${Result}
    run keyword if  ${Result} != "Recognized"      Fail    test1 Teardown

18. Associate parties to certificate
    [Tags]	Functional	certificate	create	POST    current
    Get HasAssets   Regression%20Scheme   ${Certificate_Name}
    Get HasEvaluations  Regression%20Scheme   ${Certificate_Name}
    associate parties to certificate    Certificate/Associate_Parties_RegressionCertificate.json

19. Certify certificate
    [Tags]	Functional	certificate	create	POST    current
    Certify Certificate  Certificate/Certify_RegressionCertificate.json

20. Validate Certificate Status
    [Tags]	Functional	certificate	create	current
    ${response}  Get certificate status
    log to console  ${response}
    run keyword if	${response} != "Active"	Fail	test1 Teardown


# Private Lable Part


21. Create Private Label
    [Tags]	Functional	certificate	PL  create	POST    current
    Create private label    Private_Label/CreationOfPrivateLabel_RegressionSchemeCertificate.json
    should not be empty  ${PrivateLabel_Id}
    log to console  ${PrivateLabel_Id}

22. Add Asset To Private Label
    [Tags]	Functional	certificate	PL  POST    current
    ${response}  Add Asset To PL  Private_Label/Add_Asset_To_Private_Label.json
    set global variable  ${PrivateLabel_Asset_Id}   ${response}

23. View Private Label Asset
    [Tags]	Functional	certificate	PL  POST    current
    ${result}  View Private Label Assets    ${PrivateLabel_Asset_Id}
    run keyword if  '${result}' != '${PrivateLabel_Asset_Id}'     Fail   test1 Teardown
    log to console  Private Lable Asset ID: ${result}

24. Add Party To Private Label
    [Tags]	Functional	certificate	PL  POST    current
    Add Party To PL  Private_Label/Add_Parties_To_Private_Label.json

25. Certify Private Label
    [Tags]	Functional	certificate	PL  POST    current
    Certify Private Label  Private_Label/Certify_PrivateLabelCertificate.json

26. Modify Certificate
	[Tags]	Functional	certificate create	POST    current
    Modify Certificate    Certificate/Modify_RegressionSchemeCertificate.json   ${Certificate_Id}
    run keyword if  '${Certificate_Id}' == '${Certificate_Id_Modify}'     Fail

#27. Get Certificate details from Certificate Table
#	[Tags]	Functional	certificate create	POST    current
#	Get CertificateId from Certificate Table     ${Cert_Owner_Ref_Modify}
#    run keyword if  '${Certificate_Id}, ${Certificate_Id_Modify}' != '${Cert_Id}'     Fail
#    Get Unique CertificateId from Certificate Table   ${Certificate_Id_Modify}
#    Should Not be Empty     ${Unique_Certificate_Id}
#    Get Certificate Version from Certificate Table   ${Certificate_Id_Modify}
#    run keyword if  '${Certificate_Ver}' != '2.0'     Fail





