/*
* Numenta Platform for Intelligent Computing (NuPIC)
* Copyright (C) 2015, Numenta, Inc.  Unless you have purchased from
* Numenta, Inc. a separate commercial license for this software code, the
* following terms and conditions apply:
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License version 3 as
* published by the Free Software Foundation.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
* See the GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see http://www.gnu.org/licenses.
*
* http://numenta.org/licenses/
*
*/


import UIKit
import MessageUI
/** Sliding side navigation/command menu
 */

 class MailDelegate : NSObject {
     var presentingController : UIViewController
    
    init (controller : UIViewController){
        presentingController = controller
    }
   
}
class CustomMenuController: UIViewController, UIPopoverControllerDelegate, MFMailComposeViewControllerDelegate {
    
    var presentingController : UIViewController? = nil
    
    let ABOUT = 5
    let TUTORIAL = 4
    let SETTINGS = 3
    let FEEDBACK = 1
    let SHARE = 2
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Uncomment the following line to preserve selection between presentations
        // self.clearsSelectionOnViewWillAppear = false
        
        // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
        // self.navigationItem.rightBarButtonItem = self.editButtonItem()
        
        let tapRec = UITapGestureRecognizer()
        tapRec.addTarget(self, action: "dismiss:")
        
        self.view.addGestureRecognizer(tapRec)
        
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    
   
    
   @IBAction func showTutorial(){
         show("showTutorial")
    }
    
    func show ( name : String){
       
        self.presentingController!.navigationController!.performSegueWithIdentifier (name, sender: nil)
         self.presentingController!.dismissViewControllerAnimated(false, completion: nil)
    }
    
    
    @IBAction func dismiss( sender: UIView ){
        self.presentingController!.dismissViewControllerAnimated(true, completion: nil)
    }

    @IBAction func showAbout( sender: UIView ){
      // Google Analytics
      let tracker = GAI.sharedInstance().defaultTracker
      tracker.set(kGAIScreenName, value: "com.numenta.taurus.preference.AboutActivity")
      let builder = GAIDictionaryBuilder.createScreenView()
      tracker.send(builder.build() as [NSObject : AnyObject])

      show("showAbout")
    }
    
    @IBAction func showSettings( sender: UIView ){
        if let appSettings = NSURL(string: UIApplicationOpenSettingsURLString) {
            // Google Analytics
            let tracker = GAI.sharedInstance().defaultTracker
            tracker.set(kGAIScreenName, value: "com.numenta.taurus.preference.SettingsActivity")
            let builder = GAIDictionaryBuilder.createScreenView()
            tracker.send(builder.build() as [NSObject : AnyObject])

            UIApplication.sharedApplication().openURL(appSettings)
            self.dismiss(sender)
        }
    }
    
    @IBAction func share( ){
       
        let shareService = ShareService()
        self.presentingController!.dismissViewControllerAnimated(false, completion: nil)

        shareService.share(self.presentingController!)
        
    }
    
    @IBAction func feedback(){
      
        let shareService = ShareService()
        
        self.presentingController!.dismissViewControllerAnimated(false, completion: nil)
        
        
        let mailDelegate = UIApplication.sharedApplication().delegate as! MFMailComposeViewControllerDelegate

        
      //  self.presentingController!.dismissViewControllerAnimated(false, completion: nil)
        shareService.feedback(self.presentingController!, presenter : mailDelegate)
        
    }
    
  
    
    
    static func showMenu( controller : UIViewController ){
            let storyboard : UIStoryboard = UIStoryboard(name: "Main", bundle: nil)
            let vc = storyboard.instantiateViewControllerWithIdentifier("CustomMenuController") as! CustomMenuController
            vc.modalPresentationStyle = UIModalPresentationStyle.Popover
           // let popover: UIPopoverPresentationController = vc.popoverPresentationController!
            //popover.barButtonItem = sender
            vc.modalPresentationStyle = UIModalPresentationStyle.OverCurrentContext

            vc.presentingController = controller
        
            controller.modalPresentationStyle = UIModalPresentationStyle.OverCurrentContext
            controller.presentViewController(vc, animated: true, completion:nil)

    }
    
    func adaptivePresentationStyleForPresentationController(controller: UIPresentationController) -> UIModalPresentationStyle {
        //   return UIModalPresentationStyle.FullScreen
        return UIModalPresentationStyle.Popover
        
        //  PresentationOverCurrentContext
    }
    
    
    
    
    
}
