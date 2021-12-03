import os
import imageio


def save_gif(ver=""):
    dir = r'FD_images/Snaps'
    save_dir = r'FD_images/'
    file_type = r'png'
    save_gif_name = r'Animation'
    speed_spec = {'duration': 0.05}
    if ver == "FD":
        dir = r'FD_images/Snaps'
        save_dir = r'FD_images/'
        file_type = r'png'
        save_gif_name = r'Animation'
        speed_spec = {'duration': 0.05}
    elif ver == "SA":
        dir = r'Images_SA/Snaps'
        save_dir = r'Images_SA/'
        file_type = r'png'
        save_gif_name = r'Animation'
        speed_spec = {'duration': 0.01}
    else:
        dir = r'Images_SA/Snaps'
        dir = r'Images_SA'
        save_dir = r'FD_images/'
        file_type = r'png'
        save_gif_name = r'Animation'
        speed_spec = {'duration': 0.05}

    images = []
    filenames = os.listdir(dir)
    filenames = sorted(filenames)
    for filename in filenames:
        if filename.endswith('.{}'.format(file_type)):
            file_path = os.path.join(dir, filename)
            images.append(imageio.imread(file_path))
        print(filename)
    imageio.mimsave('{}{}.gif'.format(save_dir, save_gif_name), images, **speed_spec)


def main():
    save_gif(ver="SA")
    print("save end.")


if __name__ == "__main__":
    main()
