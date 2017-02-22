#include <ros/ros.h>
#include <iostream>
#include <sstream>
#include <opencv2/opencv.hpp>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <metaroom_xml_parser/load_utilities.h>
#include <metaroom_xml_parser/simple_xml_parser.h>
#include <pcl/common/common.h>
using namespace cv;
using namespace std;
typedef pcl::PointXYZRGB PointType;

// Function for detecting and storing objects from sweeps
std::vector<Mat> readRGBImagesfromRoomSweep(const std::string &observationpath)
{
    std::vector<Mat> images;

    // Load the room xml
    //  SemanticRoom<PointType> aRoom = SemanticRoomXMLParser<PointType>::loadRoomFromXML(observationpath,true);

    // Parse the necessary clouds
    // auto sweep = SimpleXMLParser<PointType>::loadRoomFromXML(observationpath, std::vector<std::string>{"RoomCompleteCloud", "RoomIntermediateCloud"},false, true);
    // auto sweep = SimpleXMLParser<PointType>::loadRoomFromXML(observationpath, std::vector<std::string>{"RoomIntermediateCloud"},false, true);



    //   robotPosition = aRoom.getCentroid();


    std::vector<boost::shared_ptr<pcl::PointCloud<PointType>>> dat = semantic_map_load_utilties::loadIntermediateCloudsFromSingleSweep<PointType>(observationpath);

    if(dat.size() == 0)
    {
        ROS_WARN("No Intermediate clouds present!! Skipping this room!!");
        return images;
    }


    // Get the intermediate clouds
    std::vector<boost::shared_ptr<pcl::PointCloud<PointType>>> clouds = dat;//sweep.vIntermediateRoomClouds;//aRoom.getIntermediateClouds();


    // For each cloud
    for(int i = 0; i < clouds.size(); i++)
    {
        boost::shared_ptr<pcl::PointCloud<PointType>> cloud = clouds[i];



        // Create the RGB and Depth images
        std::pair<cv::Mat,cv::Mat> rgbanddepth =  SimpleXMLParser<PointType>::createRGBandDepthFromPC(cloud);


        images.push_back(rgbanddepth.first);


        // ROS_INFO("Data extracted...");
    }

    return images;
}

void saveImage(const std::string homepath,cv::Mat img,int index)
{
    std::stringstream ss;

    ss<<homepath<<"/"<<"image_"<<index<<".jpg";


    cv::imwrite(ss.str().data(),img);


    //    pcl::io::savePCDFileBinary(ss2.str().data(), cloud);



}

int main(int argc, char** argv)
{

    // bool shouldVisualize = false; // change this if you want
    // bool shouldStore = true;

    // std::vector<string> labels;

    string dataPath = "";

    // Get the data path
    if (argc >= 2)
    {
        dataPath = argv[1];
    }
    else
    {
        cout<<"Please provide data path as argument"<<endl;
        return -1;
    }

    struct stat info;

    if( stat( dataPath.data(), &info ) != 0 ){
        cout<<"cannot access "<<dataPath<<". Quitting..."<<endl;
        return -2;
    }
    else if( info.st_mode & S_IFDIR )
        cout<<dataPath<<" is a directory"<<endl;
    else
    {
        cout<<dataPath<<" is not a directory. Quitting..."<<endl;
        return -3;
    }



    /******* Initialize the ros node *******************/
    ros::init(argc, argv, "metaroom_data_extractor");

    ros::NodeHandle n;


    /**************************************************/


    struct passwd *pw = getpwuid(getuid());


    // Read the observations from XMLs
    vector<string> observations = semantic_map_load_utilties::getSweepXmls<PointType>(dataPath);

    //We now have the observation vector. Now we should parse the relevant data
    for(int i = 0; i < observations.size(); i++)
    {
        ROS_INFO("Observation path: %s",observations[i].data());

        std::vector<Mat> images = readRGBImagesfromRoomSweep(observations[i]);

        if(images.size() > 0)
        {

            const char *homedir = pw->pw_dir;

            std::string homepath(homedir);

            homepath +="/metaroom_data";

            std::stringstream ss;
            ss<<homepath<<"/"<<i;

            string command = "mkdir -p ";
            command +=ss.str();

            //std::cout<<command<<endl;

            const int dir_err = system(command.data());//mkdir(ss.str().data(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
            if (-1 == dir_err)
            {
                printf("Error creating directory!\n");
                exit(1);
            }

            std::string observationpath = ss.str();

            observationpath +="/observationpath.txt";

            ofstream f(observationpath.data());

            f<<observations[i];

            f.close();

            int count  = 0;
            for(auto image:images)
            {
                saveImage(ss.str(),image,count);
                count+=1;
            }
        }

        if(!ros::ok())
        {
            ROS_INFO("Breaking loop...");
            break;
        }

    }
    ROS_INFO("Finished inserting semantic data...");



    return 0;
}

