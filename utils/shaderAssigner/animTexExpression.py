def createAnimTexExpression(pathToFile, ownerName):
    import maya.cmds as mc
    cmd = """
    //anim tex switcher v1.1
    //expression generated by a script

    string $attribs[] = {"basecolor^1s","metalness^1s", "normal^1s",  "roughness^1s"};
    string $assetPath = "<assetPath>";  //prop path
    string $ownerName = "<ownerName>";
    string $triggerAttr = "<ownerName>.anim_tex";


    // Add zero digit padding to an int value
    global proc string pvr_zeroPadding(int $num, int $padding){ 
      // Tip from the blog post: http://ldunham.blogspot.ca/2012/01/melpython-adding-number-padding.html

      int $lengthNum=size(string($num));
      string $padString; 

      if($lengthNum<$padding){
        for($i=0;$i<($padding-$lengthNum);$i++){
          $padString=$padString+"0"; 
        }
      }
      return $padString+string($num);
    }


    for ($i=0; $i<`size $attribs`; ++$i)
    {	

        int $triggerAttrValue = `getAttr  $triggerAttr`; //extracting trigger attribute value
        string $padded = pvr_zeroPadding($triggerAttrValue, 3); //append padding to attribute

        string $materialChannel  = `format -stringArg "" $attribs[$i]`;
        string $reducedString = `format -stringArg $materialChannel -stringArg $padded $assetPath`; //generating path to texture


        string $inputAttrName = `format -stringArg "Texture" $attribs[$i]`; //generate input attribute name
        string $inputAttrFullPath =  `format -stringArg $ownerName  -stringArg $inputAttrName "^1s.^2s"`; //append attribute name to its owner
        setAttr -type "string" $inputAttrFullPath $reducedString; //set parameter
    }
    <ownerName>.buffer = <ownerName>.anim_tex;
    """
    cmd = cmd.replace ('<assetPath>', pathToFile)
    cmd = cmd.replace ('<ownerName>', ownerName)

    mc.expression (s=cmd)


if __name__=='__main__':
    pathToFile = '${ENOTKI}\\assets\\props\\prop_crayon_a\\tex\\animation_textures\\output\prop_crayon_a_^1s.<UDIM>.^2s.exr'
    ownerName = 'prop_crayon_a_rs_mt_01'
    createAnimTexExpression(pathToFile, ownerName)