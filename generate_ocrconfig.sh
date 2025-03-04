######
# $1 = state_code in lower case
# $2 = "starting_text,ending_text" comma separated text
# $3 = True or False i.e. whether to enable translation or not

stateCode=$( echo $1 )

customiseMetaConfig() {
  stateCode=$( echo $1 )
  replacementLine=$( echo $2 )
  sedString=$( echo $3 )
  parameterStateCode=$( echo $3 | cut -d':' -f1 )
  parametersToReplace=$( echo $3 | cut -d':' -f2 )
  if [ "$stateCode" = "$parameterStateCode" ]
  then
    for param in $(echo $parametersToReplace | sed "s/,/ /g")
    do
      parameterToReplace=$( echo $param | cut -d'=' -f1 )
      value=$( echo $param | cut -d'=' -f2 )
      replacementSubString=$( echo "$replacementSubString;s/\\\$$parameterToReplace/$value/g" )
    done
  fi
  echo $replacementLine | sed "$replacementSubString"
}

replacementLine="s/@@statename@@/\$stateCode/g;s/@@yInterval@@/\$yInterval/g;s/@@xInterval@@/\$xInterval/g;s/@@houghTransform@@/\$houghTransform/g;s/@@enableTranslation@@/\$enableTranslation/g;s/@@startingText@@/\$startingText/g;s/@@configMinLineLength@@/\$configMinLineLength/g;"

replacementLine=$( customiseMetaConfig $stateCode $replacementLine "hp:houghTransform=False,yInterval=5" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "br:houghTransform=False" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "mp:houghTransform=False" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "ap:configMinLineLength=300" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "tn:configMinLineLength=500" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "tg:enableTranslation=True" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "mz:houghTransform=False" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "ml:configMinLineLength=250" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "ut:houghTransform=False" )
replacementLine=$( customiseMetaConfig $stateCode $replacementLine "nl:configMinLineLength=250" )

configMinLineLength=400
startingText=`echo $2`
enableTranslation=`echo $3`
houghTransform="True"
yInterval=0
xInterval=0

finalReplacementString=$( echo $replacementLine | sed "s/\$stateCode/$stateCode/g; s/\$yInterval/$yInterval/g; s/\$xInterval/$xInterval/g; s/\$houghTransform/$houghTransform/g; s/\$enableTranslation/$enableTranslation/g; s/\$startingText/$startingText/g; s/\$configMinLineLength/$configMinLineLength/g" )

echo $finalReplacementString

sed "$finalReplacementString" ocrconfig.meta.orig > ocrconfig.meta