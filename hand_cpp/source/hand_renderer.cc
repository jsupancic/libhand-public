// Copyright (c) 2011, Marin Saric <marin.saric@gmail.com>
// All rights reserved.
//
// This file is a part of LibHand. LibHand is open-source software. You can
// redistribute it and/or modify it under the terms of the LibHand
// license. The LibHand license is the BSD license with an added clause that
// requires academic citation. You should have received a copy of the
// LibHand license (the license.txt file) along with LibHand. If not, see
// <http://www.libhand.org/>
//
// HandRenderer

# include "hand_renderer.h"

# include <cmath>

# include <exception>
# include <stdexcept>
# include <iostream>
# include <vector>

# include <boost/shared_ptr.hpp>
# include <boost/shared_array.hpp>

# include "OGRE/OgreQuaternion.h"
# include "OGRE/OgreVector3.h"
# include "OGRE/OgreMatrix3.h"

# include "OGRE/OgreRoot.h"
# include "OGRE/OgreRenderSystem.h"
# include "OGRE/OgreRenderWindow.h"
# include "OGRE/OgreSceneManager.h"
# include "OGRE/OgreTextureManager.h"
# include "OGRE/OgreTexture.h"
# include "OGRE/OgreHardwarePixelBuffer.h"

# include "OGRE/OgreEntity.h"
# include "OGRE/OgreBone.h"
# include "OGRE/OgreSkeleton.h"
#include <OGRE/OgreTagPoint.h>

# include "OgreGLPlugin.h"
# include "OgreOctreePlugin.h"

# include "dot_sceneloader.h"
# include "hand_camera_spec.h"
# include "hand_pose.h"

#include "OgreGpuCommandBufferFlush.hpp"

#if __APPLE__ & __MACH__
# include "mac_app_loop.h"
#endif

# include "printfstring.h"

# include "opencv2/opencv.hpp"

namespace libhand {

using namespace std;
using namespace boost;
using namespace Ogre;

class HandRendererPrivate {
 public:
  HandRendererPrivate();

  static const int kDefaultWidth = HandRenderer::kDefaultWidth;
  static const int kDefaultHeight = HandRenderer::kDefaultHeight;
  
  void Setup(int width = kDefaultWidth,
             int height = kDefaultHeight);

  void SetRenderSize(int width = kDefaultWidth,
                     int height = kDefaultHeight);

  void LoadScene(const SceneSpec &scene_spec);

  void SetHandPose(const FullHandPose &hand_pose, bool update_camera);

  void RenderHand();

  int render_width() const { return render_width_; }
  int render_height() const { return render_height_; }

  const char *pixel_buffer_raw() const {
    return pixel_data_.get();
  }

  const cv::Mat pixel_buffer_cv() const;
  const cv::Mat depth_buffer_cv() const;

  float initial_cam_distance() const { return initial_cam_distance_; }
  float CameraHandDistance();

  HandCameraSpec camera_spec() const { return camera_spec_; }
  void set_camera_spec(const HandCameraSpec &camera_spec) {
    camera_spec_ = camera_spec;
    
    Vector3 camera_pos_world =
      ( hand_node_->convertLocalToWorldPosition(Vector3::ZERO)
	+ camera_spec_.GetPosition() );
    camera_node_->setPosition(camera_pos_world);
    camera_->setOrientation(camera_spec_.GetQuaternion());
//     cout << "camera_spec_pos: " << 
//       " r: " << camera_spec_.r << 
//       " phi: " << camera_spec_.phi << 
//       " theta: " << camera_spec_.theta << endl;;  
//     cout << "camera_pos_world: " << 
//       " x: " << camera_pos_world.x << 
//       " y: " << camera_pos_world.y << 
//       " z: " << camera_pos_world.z << endl;
//     cout << "hand_node_pos: " << 
//       " x: " << hand_node_->getPosition().x << 
//       " y: " << hand_node_->getPosition().x << 
//       " z: " << hand_node_->getPosition().x << endl;;        
  }

  // http://www.ogre3d.org/forums/viewtopic.php?t=36034&highlight=
  void get2dposition(
    const Ogre::Vector3 &position, 
    Ogre::Real &x, Ogre::Real &y, Ogre::Real& z)
  {
    Ogre::Vector3 worldview = camera_->getViewMatrix() * position;
    z = worldview.z;
    //homogenous clip space, between -1, 1 is in frustum
    Ogre::Vector3 hcsposition = camera_->getProjectionMatrix() * worldview;

    /* absolute */
    x = render_width() / 2;
    y = render_height() / 2;
    x += ( x * hcsposition.x );
    y += ( y * -hcsposition.y );
  }

  // http://www.ogre3d.org/forums/viewtopic.php?f=1&t=55259
  // http://www.ogre3d.org/forums/viewtopic.php?f=2&t=49051
  Vector3 getBoneWorldPosition(Bone*bone,Entity*entity)
  {
    //[bone] = bone for which you are trying to get the world position [Bone*].
    //[entity] = The entity to which the bone's skeleton belongs to [Entity*].
    //[world position] = output parameter [Vector3].

    Vector3 world_position = bone->_getDerivedPosition(); 

    //multiply with the parent derived transformation
    Ogre::Node* pParentNode = entity->getParentNode();
    Ogre::Node* pSceneNode = entity->getParentSceneNode();
    while (pParentNode != NULL) 
    {
      //process the current i_Node
      if (pParentNode != pSceneNode)
      {
	  //this is a tag point (a connection point between 2 entities). which means it has a parent i_Node to be processed
	  world_position = dynamic_cast<Ogre::TagPoint*>(pParentNode)->_getFullLocalTransform() * world_position;
	  pParentNode = dynamic_cast<Ogre::TagPoint*>(pParentNode)->getParentEntity()->getParentNode();
      }
      else
      {
	  //this is the scene i_Node meaning this is the last i_Node to process
	  world_position = pParentNode->_getFullTransform() * world_position;
	  break;
      }
    }
    
    return world_position;
  }  
  
  // http://www.ogre3d.org/forums/viewtopic.php?f=1&t=55259
  Quaternion GetBoneWorldOrientation(Bone*bone,Entity*ent)
  {
      Quaternion world_orientation = bone->_getDerivedOrientation();

      //multiply with the parent derived transformation
      Node*pParentNode = ent->getParentNode();
      SceneNode*pSceneNode = ent->getParentSceneNode();
      while (pParentNode != NULL)
      {
	  //process the current i_Node
	  if (pParentNode != pSceneNode)
	  {
	      //this is a tag point (a connection point between 2 entities). which means it has a parent i_Node to be processed
	      world_orientation = 
		dynamic_cast<Ogre::TagPoint*>(pParentNode)->_getDerivedOrientation() * world_orientation;
	      pParentNode = dynamic_cast<Ogre::TagPoint*>(pParentNode)->getParentEntity()->getParentNode();
	  }
	  else
	  {
	      //this is the scene i_Node meaning this is the last i_Node to process
	      world_orientation = pParentNode->_getDerivedOrientation() * world_orientation;
	      break;
	  }
      }
      return world_orientation;
  }  
  
  void emit_bone(
    int depth, double screen_x, double screen_y, double screen_z,
    string name, Vector3 pos_world,
    HandRenderer::JointPositionMap&jointPositionMap)
  {
//     for(int iter = 0; iter < depth; iter++)
//       printf("\t");
//     printf("r(%s) @ (%f %f %f)\n",name.c_str(),
// 	   (double)screen_x,(double)screen_y,(double)0);
//     for(int iter = 0; iter < depth; iter++)
//       printf("\t");    
//     printf("w(%s) @ (%f %f %f)\n",name.c_str(),
// 	(double)pos_world.x,(double)pos_world.y,(double)pos_world.z);
    jointPositionMap[name] = cv::Vec3d(
      (double)screen_x,(double)screen_y,(double)screen_z);    
  }
  
  void walk_bones(HandRenderer::JointPositionMap&jointPositionMap,Node* bone = NULL,int depth = 0)
  {
    // default to the root bone
    if(bone == NULL)
    {
      bone = hand_skeleton_->getRootBone();
      // print the BB as well
      AxisAlignedBox bb = hand_entity_->getBoundingBox();
      //cout << "hand radius: " << hand_entity_->getBoundingRadius() << endl;
    }
    
    // print the bone's info
    string name = bone->getName();
    //Vector3 position = Vector3(0,0,0);
    //Vector3 position = bone->getPosition(); // NOTE: rel to parent, maybe should be zero for all?
    //Vector3 pos_world = bone->convertLocalToWorldPosition(position);
    Vector3 pos_world = getBoneWorldPosition(dynamic_cast<Bone*>(bone),hand_entity_);
    // converto nsc
    Real screen_x, screen_y, screen_z; 
    get2dposition(pos_world, screen_x,screen_y,screen_z);
    
    // store the bone  information
    // bones ~ joints in Ogre nomenclature
    emit_bone(depth, screen_x, screen_y, screen_z, name, pos_world,jointPositionMap);
    
    // call recursively on the children
    if(bone->numChildren() == 0)
    {
      // is finger tip?
      Vector3 step = GetBoneWorldOrientation(dynamic_cast<Bone*>(bone),hand_entity_)
	.yAxis().normalisedCopy();
      Vector3 tip_pos = pos_world + .4*step;
      
      // write the 2d position of the finger tip
      get2dposition(tip_pos, screen_x,screen_y,screen_z);
      emit_bone(depth + 1, screen_x, screen_y, screen_z, name + "tip", tip_pos,jointPositionMap);    
    }
    else
    {
      for(int child_iter = 0; child_iter < bone->numChildren(); child_iter++)
	walk_bones(jointPositionMap,bone->getChild(child_iter),depth+1);
    }
  }
  
  bool z_inverted() const;
 private:
  void SetRenderSizeInternal(int width, int height);
  void DestroyScene();
  void InitChecks();

  Vector3 CamPositionRelativeToHand();

#if __APPLE__ & __MACH__
  MacMemoryPool mac_memory_pool;
#endif

  int id;
  bool renderer_is_setup_;
  bool scene_is_loaded_;

  int render_width_;
  int render_height_;

  const string render_tex_rsrc_name_;
  const string render_tex_name_;

  const string scene_rsrc_name_;

  shared_array<char> pixel_data_;
  //shared_ptr<GLPlugin> gl_plugin_;
  //shared_ptr<OctreePlugin> octree_plugin_;

  SceneSpec scene_spec_;

  SceneManager *scene_mgr_;
  ResourceGroupManager *resource_mgr_;

  RenderTexture *render_target_;
  TexturePtr output_texture_;

  Camera *camera_;
  Node *camera_node_;
  Viewport *viewport_;
  Entity *hand_entity_;
  Node *hand_node_;
  Skeleton *hand_skeleton_;

  float initial_cam_distance_;
  HandCameraSpec camera_spec_;

  std::vector<Bone *> bone_by_index_;

  // Disallow
  HandRendererPrivate(const HandRendererPrivate &rhs);
  HandRendererPrivate& operator= (const HandRendererPrivate &rhs);
  
  friend class HandRenderer;
};

// singleton
static boost::shared_ptr<Root> root_;
static boost::shared_ptr<RenderWindow> window_;

// Forwarding HandRenderer calls to HandRendererPrivate
HandRenderer::HandRenderer() : private_(new HandRendererPrivate) {}
HandRenderer::~HandRenderer() { delete private_; }

void HandRenderer::walk_bones(HandRenderer::JointPositionMap&jointPositionMap)
{
  private_->walk_bones(jointPositionMap);
  //jointPositionMap.erase(jointPositionMap.find("root"));
}

void HandRenderer::Setup(int width, int height) {
  private_->Setup(width, height);
}
void HandRenderer::SetRenderSize(int width, int height) {
  private_->SetRenderSize(width, height);
}
void HandRenderer::LoadScene(const SceneSpec &scene_spec) {
  private_->LoadScene(scene_spec);
}
void HandRenderer::SetHandPose(const FullHandPose &hand_pose,
                               bool update_camera) {
  private_->SetHandPose(hand_pose, update_camera);
}
void HandRenderer::RenderHand() { private_->RenderHand(); }

float HandRenderer::initial_cam_distance() const {
  return private_->initial_cam_distance();
}
HandCameraSpec HandRenderer::camera_spec() const {
  return private_->camera_spec();
}
void HandRenderer::set_camera_spec(const HandCameraSpec &camera_spec) {
  private_->set_camera_spec(camera_spec);
}

int HandRenderer::render_width() const { return private_->render_width(); }
int HandRenderer::render_height() const { return private_->render_height(); }

const char *HandRenderer::pixel_buffer_raw() const {
  return private_->pixel_buffer_raw();
}
const cv::Mat HandRenderer::pixel_buffer_cv() const {
  return private_->pixel_buffer_cv();
}
const cv::Mat HandRenderer::depth_buffer_cv() const {
  return private_->depth_buffer_cv();
}
// End of forwarding HandRenderer calls to HandRendererPrivate

static int renderer_counter = 0;

template<typename T>
string to_string(T v)
{
  ostringstream oss;
  oss << v;
  return oss.str();
}

HandRendererPrivate::HandRendererPrivate() :
  renderer_is_setup_(false),
  scene_is_loaded_(false),
  render_width_(0),
  render_height_(0),
  id(renderer_counter++),
  render_tex_rsrc_name_(to_string(id) + "HandRenderer RenderTexture Resources"),
  render_tex_name_(to_string(id) + "HandRenderer RenderTexture"),
  scene_rsrc_name_(to_string(id) + "HandRenderer Scene Resources"),
  //gl_plugin_(new GLPlugin),
  //octree_plugin_(new OctreePlugin),
  scene_mgr_(NULL),
  resource_mgr_(NULL),
  render_target_(NULL),
  camera_(NULL),
  camera_node_(NULL),
  viewport_(NULL),
  hand_entity_(NULL),
  hand_node_(NULL),
  hand_skeleton_(NULL),
  initial_cam_distance_(0) {
}

void HandRendererPrivate::Setup(int width, int height) {
  if (width <= 0 || height <= 0) {
    throw runtime_error("Bad HandRenderer render width or height");
  }

  if (renderer_is_setup_) {
    SetRenderSize(width, height);
    return;
  }

  //gl_plugin_.reset(new GLPlugin);
  //octree_plugin_.reset(new OctreePlugin);

  if(!root_)
  {
    root_.reset(new Root("", "", "hand_renderer.log"));

    //root_->installPlugin(gl_plugin_.get());
    //root_->installPlugin(octree_plugin_.get());
    root_->loadPlugin("/usr/lib64/OGRE/RenderSystem_GL.so");
    root_->loadPlugin("/usr/lib64/OGRE/Plugin_OctreeSceneManager.so");

    RenderSystemList render_systems = root_->getAvailableRenderers();
    if (!render_systems.size()) {
      throw runtime_error("No rendersystem found..");
    }

    RenderSystem *render_system = render_systems[0];
    root_->setRenderSystem(render_system);

    render_system = root_->getRenderSystem();

    root_->initialise(false, "");
  }

  scene_mgr_ = root_->createSceneManager(Ogre::ST_GENERIC);

  resource_mgr_ = ResourceGroupManager::getSingletonPtr();
  resource_mgr_->createResourceGroup(render_tex_rsrc_name_);
  resource_mgr_->initialiseResourceGroup(render_tex_rsrc_name_);

  NameValuePairList window_params;
  window_params["macAPI"] = "cocoa";

  if(!window_)
  {
    RenderWindow * window = (root_->createRenderWindow("HandRenderer Window",
						  1, 1,
						  false,
						  &window_params));
    window->setVisible(false);
    window_.reset(window);
  }
  
  SetRenderSizeInternal(width, height);

  renderer_is_setup_ = true;

  static GpuCommandBufferFlush flusher;
  if(!flusher.isStarted())
    flusher.start(1);
}

void HandRendererPrivate::SetRenderSizeInternal(int width, int height) {
  pixel_data_.reset(new char[3 * width * height]);

  output_texture_ =
    TextureManager::getSingleton().createManual(render_tex_name_,
                                                render_tex_rsrc_name_,
                                                TEX_TYPE_2D,
                                                width, height,
                                                0,
                                                PF_B8G8R8,
                                                TU_RENDERTARGET,
                                                0, false, false);

  render_target_ = output_texture_->getBuffer()->getRenderTarget();
  render_width_ = width; render_height_ = height;
}

void HandRendererPrivate::SetRenderSize(int width, int height) {
  if (!renderer_is_setup_) {
    Setup(width, height);
    return;
  }

  if (width == render_width_ && height == render_height_) {
    return;
  }

  if (!output_texture_.isNull()) {
    TextureManager::getSingleton().remove(render_tex_name_);
    output_texture_.setNull();
  }

  SetRenderSizeInternal(width, height);
}

void HandRendererPrivate::LoadScene(const SceneSpec &scene_spec) {
  if (!renderer_is_setup_) {
    Setup(kDefaultWidth, kDefaultHeight);
  }

  if (!scene_spec.IsComplete()) {
    throw runtime_error("The scene spec is not complete");
  }

  if (scene_is_loaded_) {
    DestroyScene();
  }

  resource_mgr_->createResourceGroup(scene_rsrc_name_);

  try {
    resource_mgr_->addResourceLocation(scene_spec.SceneDirFullPath(),
                                       "FileSystem",
                                       scene_rsrc_name_,
                                       false);
    resource_mgr_->initialiseResourceGroup(scene_rsrc_name_);
    resource_mgr_->loadResourceGroup(scene_rsrc_name_);

    if (!resource_mgr_->resourceExists(scene_rsrc_name_,
                                       scene_spec.scene_file())) {
      throw runtime_error(PrintFString
                          ("The scene file %s does not appear to exist "
                           "in directory %s",
                           scene_spec.scene_file().c_str(),
                           scene_spec.SceneDirFullPath().c_str()));
    }

    DotSceneLoader scene_loader;
    
    scene_loader.parseDotScene(scene_spec.scene_file(),
                               scene_rsrc_name_, scene_mgr_);

    SceneManager::CameraIterator cameras = scene_mgr_->getCameraIterator();
    if (!cameras.hasMoreElements()) {
      throw runtime_error("The scene does not have a camera!");
    }

    camera_ = cameras.getNext();

    camera_node_ = camera_->getParentNode();
    if (!camera_node_) {
      throw runtime_error("The camera is not attached to a node!");
    }

    if (!scene_mgr_->hasEntity(scene_spec.hand_object_name())) {
      throw runtime_error(PrintFString("The scene does not have the object %s",
                                       scene_spec.hand_object_name().c_str()));
    }

    hand_entity_ = scene_mgr_->getEntity(scene_spec.hand_object_name());
    if (!hand_entity_->hasSkeleton()) {
      throw runtime_error(PrintFString
                          ("The hand object %s does not have a skeleton.",
                           scene_spec.hand_object_name().c_str()));
    }

    hand_node_ = hand_entity_->getParentNode();
    if (!hand_node_) {
      throw runtime_error("The hand entity object is not attached to a node");
    }

    hand_skeleton_ = hand_entity_->getSkeleton();

    viewport_ = render_target_->addViewport(camera_);
    viewport_->setBackgroundColour(ColourValue(0, 0, 0));

    for (int i = 0; i < scene_spec.num_bones(); ++i) {
      const string &bone_name = scene_spec.bone_name(i);

      if (!hand_skeleton_->hasBone(bone_name)) {
        throw runtime_error(PrintFString
                            ("The hand object %s does not have a "
                             "bone named %s",
                             scene_spec.hand_object_name().c_str(),
                             bone_name.c_str()));
      }
      Bone *bone = hand_skeleton_->getBone(bone_name);
      bone->setManuallyControlled(true);

      bone_by_index_.push_back(bone);
    }

    initial_cam_distance_ = CameraHandDistance();
    camera_spec_= HandCameraSpec(initial_cam_distance());

    camera_node_->setPosition(0,0,0);
    camera_node_->resetOrientation();
    camera_node_->setInheritOrientation(false);
    camera_->setPosition(0,0,0);
    camera_->setOrientation(Quaternion::IDENTITY);
    // use FOV for ASUS Xtion.
    camera_->setFOVy(Ogre::Radian(0.785398163));
    double aspect_ratio = std::tan(1.01229097/2)/std::tan(0.785398163/2);
    camera_->setAspectRatio(aspect_ratio);
  } catch(...) {
    DestroyScene();

    throw;
  }

  scene_spec_ = scene_spec;
  //cout << "scene_spec_.num_bones = " << scene_spec_.num_bones() << endl;
  scene_is_loaded_ = true;
}

void HandRendererPrivate::DestroyScene() {
  render_target_->removeAllViewports();
  scene_mgr_->destroyAllCameras();
  scene_mgr_->clearScene();
  resource_mgr_->destroyResourceGroup(scene_rsrc_name_);
  bone_by_index_.clear();
  scene_is_loaded_ = false;
}

void HandRendererPrivate::InitChecks() {
  if (!renderer_is_setup_) {
    Setup(kDefaultWidth, kDefaultHeight);
  }

  if (!scene_is_loaded_) {
    throw runtime_error("No scene loaded...");
  }
}

void HandRendererPrivate::SetHandPose(const FullHandPose &hand_pose,
                                      bool update_camera) {
  InitChecks();

  if (hand_pose.num_joints() != scene_spec_.num_bones()) {
    throw runtime_error(PrintFString("The bone map has %d bones, while "
                                     "the number of joints in the hand pose "
                                     "is %d", scene_spec_.num_bones(),
                                     hand_pose.num_joints()));
  }

  hand_skeleton_->reset(true);

  for (int bone_no = 0; bone_no < scene_spec_.num_bones(); ++bone_no) {
    Bone *bone = bone_by_index_[bone_no];
    HandJoint joint_angle = hand_pose.joint(bone_no);

    bone->rotate(joint_angle.ToQuaternion(), Node::TS_LOCAL);
    //bone->setInheritScale(false);
    //bone->setScale(Ogre::Vector3(joint_angle.swelling,joint_angle.elongation, joint_angle.dilation));
  }

  if (update_camera) {
    camera_spec_.SetFromHandPose(hand_pose);
  }
}

bool HandRenderer::z_inverted() const
{
  return private_->z_inverted();
}

bool HandRendererPrivate::z_inverted() const
{
  return camera_node_->getPosition().z < 0;  
}

double HandRenderer::z_far() const
{
  return private_->camera_->getFarClipDistance();
}

double HandRenderer::z_near() const
{
  return private_->camera_->getNearClipDistance();
}



void HandRendererPrivate::RenderHand() {
  InitChecks();
    
//   hand_node_->setPosition(camera_spec_.GetPosition());
  //Vector3 pos = camera_spec_.GetPosition();
  //cout << "hand position: " << pos.x << ", " << pos.y << ", " << pos.z << endl;
//   hand_node_->setOrientation(camera_spec_.GetQuaternion());
//   
//   camera_node_->setPosition(Vector3::ZERO);
//   camera_->lookAt(hand_node_->getPosition());
  
  viewport_->clear();
  root_->renderOneFrame();
  //render_target_->update(false);
  viewport_->update();
  PixelBox pixel_box(Box(0, 0, render_width_, render_height_),
                     PF_R8G8B8,
                     pixel_data_.get());
  render_target_->copyContentsToMemory(pixel_box, RenderTarget::FB_FRONT);
}

const cv::Mat HandRendererPrivate::pixel_buffer_cv() const {
  return cv::Mat(render_height_, render_width_, CV_8UC3, pixel_data_.get());
}

  static std::vector<float> unprojectZ(const int W, const int H, std::vector<float>& Z)
  {
    std::vector<float> Zout(W*H);
    
    // unproject Z distances to world coordinate system distances
    //GLdouble MV[4*4];
    GLdouble PROJ[4*4];
    int VP[4]; // w x w h
    // set MV matrix to identity glGetDoublev(GL_MODELVIEW_MATRIX, MV);
    cv::Mat eye4 = cv::Mat::eye(4,4,CV_64F);
    glGetDoublev(GL_PROJECTION_MATRIX,PROJ);
    glGetIntegerv(GL_VIEWPORT,VP);
    for(int xIter = 0; xIter < W; xIter++)
    {
      for(int yIter = 0; yIter < H; yIter++)
      {
	// pixels are row-major ordered
	float z = Z[xIter + (yIter)*W];
	if(z < 1)
	{
	  double oX, oY, oZ;
	  gluUnProject(xIter,yIter,z,
		      eye4.ptr<double>(0),PROJ,VP,&oX,&oY,&oZ);
	  Zout[xIter + (H-1-yIter)*W] = -oZ;
	}
	else
	  Zout[xIter + (H-1-yIter)*W] = numeric_limits<float>::infinity();
      }
    }    
    
    return Zout;
  }
  
static void gl_cv_read_buffers_Z(cv::Mat&Zrnd,int W,int H)
{
  // get the depth buffer.
  std::vector<float> Z(W*H);
  glFinish();
  glReadPixels(0,0,W,H,GL_DEPTH_COMPONENT,GL_FLOAT,&Z[0]);
  glFinish();

  Z = unprojectZ(W,H, Z);    
  //Z = allocRawZ(W,H,Z);
    
  // convet to OCV
  Zrnd = cv::Mat_<float>(H,W,&Z[0]).clone();
}
  
const cv::Mat HandRendererPrivate::depth_buffer_cv() const
{
  int W = render_width();
  int H = render_height();
  cv::Mat depth_data = cv::Mat(H,W,cv::DataType<float>::type,cv::Scalar::all(std::numeric_limits<float>::infinity()));
  gl_cv_read_buffers_Z(depth_data,W,H);
  cv::flip(depth_data,depth_data,0);
  return depth_data;
}

Vector3 HandRendererPrivate::CamPositionRelativeToHand() {
  Vector3 camera_pos_world = camera_->getDerivedPosition();
  Vector3 hand_pos_world = hand_node_->convertLocalToWorldPosition(Vector3(0,0,0));

  return camera_pos_world - hand_pos_world;
}

float HandRendererPrivate::CameraHandDistance() {
  return CamPositionRelativeToHand().length();
}

}  // namespace libhand
